import { useEffect, useState } from "react";
import {
  Container,
  Paper,
  Title,
  Text,
  Button,
  Group,
  Select,
  TextInput,
  NumberInput,
  Divider,
  Alert,
  Stack,
  Card,
  Badge,
  Table,
} from "@mantine/core";
import { useNavigate } from "react-router-dom";

export default function TeacherDashboard() {
  const navigate = useNavigate();

  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState(null);

  // Create class
  const [name, setName] = useState("");
  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  const [radiusMeters, setRadiusMeters] = useState(50);

  // Attendance
  const [attendanceCode, setAttendanceCode] = useState("ABC123");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [activeSession, setActiveSession] = useState(null);
  const [records, setRecords] = useState(null);

  const [error, setError] = useState(null);
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const logout = async () => {
    await fetch("/auth/logout", { method: "POST", credentials: "include" });
    navigate("/login");
  };

  const loadClasses = async () => {
    const res = await fetch("/classes", { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load classes");
    setClasses(data.classes || []);
    if ((data.classes || []).length > 0 && !selectedClassId) {
      setSelectedClassId(data.classes[0].id);
    }
  };

  const loadActiveSession = async (classId) => {
    if (!classId) return;
    const res = await fetch(`/attendance/active?class_id=${classId}`, {
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load active session");
    setActiveSession(data.active);
  };

  useEffect(() => {
    (async () => {
      try {
        setError(null);
        await loadClasses();
      } catch (e) {
        setError(e.message);
      }
    })();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    (async () => {
      try {
        setError(null);
        setMsg(null);
        setRecords(null);
        await loadActiveSession(selectedClassId);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [selectedClassId]);

  const useMyLocation = () => {
    setError(null);
    setMsg(null);
    if (!navigator.geolocation) {
      setError("Geolocation not supported.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(pos.coords.latitude);
        setLongitude(pos.coords.longitude);
        setMsg("Location filled from browser.");
      },
      () => setError("Location permission denied or unavailable.")
    );
  };

  const createClass = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      const payload = {
        name,
        latitude,
        longitude,
        radius_meters: radiusMeters,
      };

      const res = await fetch("/classes", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to create class");

      setMsg(`Class created (id: ${data.class_id}).`);
      setName("");
      await loadClasses();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const startAttendance = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      if (!selectedClassId) throw new Error("Select a class first.");

      const s = startsAt || "2026-01-01T00:00:00";
      const e = endsAt || "2027-01-01T00:00:00";

      const payload = {
        class_id: selectedClassId,
        attendance_code: attendanceCode,
        starts_at: s,
        ends_at: e,
      };

      const res = await fetch("/attendance/start", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to start attendance");

      setMsg(`Attendance started (session id: ${data.attendance_session_id}).`);
      await loadActiveSession(selectedClassId);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const endAttendance = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      if (!activeSession) throw new Error("No active session to end.");

      const res = await fetch("/attendance/end", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          attendance_session_id: activeSession.attendance_session_id,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to end attendance");

      setMsg("Attendance session ended.");
      setActiveSession(null);
      setRecords(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadRecords = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      if (!activeSession) throw new Error("No active session to view records.");

      const res = await fetch(
        `/attendance/session/${activeSession.attendance_session_id}/records`,
        { credentials: "include" }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load records");

      setRecords(data);
      setMsg(`Loaded ${data.count} record(s).`);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const classOptions = classes.map((c) => ({
    value: String(c.id),
    label: `#${c.id} - ${c.name}`,
  }));

  return (
    <Container size="lg" my={30}>
      <Group justify="space-between" mb="md">
        <div>
          <Title order={2}>Teacher Dashboard</Title>
          <Text c="dimmed">Manage classes and attendance sessions</Text>
        </div>
        <Button variant="light" color="red" onClick={logout}>
          Logout
        </Button>
      </Group>

      {error && (
        <Alert color="red" title="Error" mb="md">
          {error}
        </Alert>
      )}
      {msg && (
        <Alert color="green" title="Success" mb="md">
          {msg}
        </Alert>
      )}

      <Paper withBorder p="md" radius="md">
        <Title order={4}>Create Class</Title>
        <Divider my="sm" />

        <Stack>
          <TextInput label="Class name" value={name} onChange={(e) => setName(e.target.value)} />
          <Group grow>
            <NumberInput label="Latitude" value={latitude} onChange={setLatitude} />
            <NumberInput label="Longitude" value={longitude} onChange={setLongitude} />
          </Group>
          <NumberInput label="Radius (meters)" value={radiusMeters} onChange={setRadiusMeters} min={1} />

          <Group>
            <Button variant="light" onClick={useMyLocation}>
              Use my location
            </Button>
            <Button onClick={createClass} loading={loading}>
              Create Class
            </Button>
          </Group>
        </Stack>
      </Paper>

      <Divider my="lg" />

      <Paper withBorder p="md" radius="md">
        <Group justify="space-between" mb="sm">
          <Title order={4}>Attendance</Title>
          <Badge color={activeSession ? "green" : "gray"}>
            {activeSession ? `Active Session #${activeSession.attendance_session_id}` : "No Active Session"}
          </Badge>
        </Group>

        <Select
          label="Select class"
          placeholder="Choose a class"
          data={classOptions}
          value={selectedClassId ? String(selectedClassId) : null}
          onChange={(val) => setSelectedClassId(val ? parseInt(val) : null)}
          searchable
        />

        <Divider my="sm" />

        <Group grow>
          <TextInput
            label="Attendance code"
            value={attendanceCode}
            onChange={(e) => setAttendanceCode(e.target.value)}
          />
          <TextInput
            label="Starts at (optional)"
            placeholder="YYYY-MM-DDTHH:MM:SS"
            value={startsAt}
            onChange={(e) => setStartsAt(e.target.value)}
          />
          <TextInput
            label="Ends at (optional)"
            placeholder="YYYY-MM-DDTHH:MM:SS"
            value={endsAt}
            onChange={(e) => setEndsAt(e.target.value)}
          />
        </Group>

        <Group mt="md">
          <Button onClick={startAttendance} loading={loading}>
            Start Attendance
          </Button>
          <Button variant="outline" color="red" onClick={endAttendance} disabled={!activeSession} loading={loading}>
            End Attendance
          </Button>
          <Button variant="light" onClick={loadRecords} disabled={!activeSession} loading={loading}>
            View Records
          </Button>
        </Group>

        {records && (
          <>
            <Divider my="md" />
            <Card withBorder radius="md">
              <Title order={5}>Records</Title>
              <Text c="dimmed" mb="sm">
                Session #{records.attendance_session_id} — Total: {records.count}
              </Text>

              <Table striped highlightOnHover withTableBorder withColumnBorders>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Student ID</Table.Th>
                    <Table.Th>Status</Table.Th>
                    <Table.Th>Marked At</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {records.records.map((r) => (
                    <Table.Tr key={r.id}>
                      <Table.Td>{r.student_id}</Table.Td>
                      <Table.Td>{r.status}</Table.Td>
                      <Table.Td>{r.marked_at}</Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Card>
          </>
        )}
      </Paper>
    </Container>
  );
}
