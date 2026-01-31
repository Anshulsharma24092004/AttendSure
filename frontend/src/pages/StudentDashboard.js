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
  Divider,
  Alert,
  Stack,
  Card,
  Badge,
  Table,
} from "@mantine/core";
import { useNavigate } from "react-router-dom";

export default function StudentDashboard() {
  const navigate = useNavigate();

  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState(null);

  // enroll
  const [enrollClassId, setEnrollClassId] = useState("");

  // active session
  const [activeSession, setActiveSession] = useState(null);

  // submit
  const [attendanceCode, setAttendanceCode] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

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

  const checkActiveSession = async (classId) => {
    if (!classId) return;
    const res = await fetch(`/attendance/active?class_id=${classId}`, {
      credentials: "include",
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch active session");
    setActiveSession(data.active); // may be null
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
        setActiveSession(null);
        if (selectedClassId) await checkActiveSession(selectedClassId);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [selectedClassId]);

  const enroll = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      const cid = parseInt(enrollClassId);
      if (!cid) throw new Error("Enter a valid class_id (e.g., 1).");

      const res = await fetch(`/classes/${cid}/enroll`, {
        method: "POST",
        credentials: "include",
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to enroll");

      setMsg(data.message || "Enrolled successfully.");
      setEnrollClassId("");
      await loadClasses();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const getMyLocation = () => {
    setError(null);
    setMsg(null);

    if (!navigator.geolocation) {
      setError("Geolocation not supported in this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(pos.coords.latitude.toString());
        setLongitude(pos.coords.longitude.toString());
        setMsg("Location captured successfully.");
      },
      () => setError("Could not fetch location. Allow location permission.")
    );
  };

  const submitAttendance = async () => {
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      if (!selectedClassId) throw new Error("Select a class first.");
      if (!activeSession)
        throw new Error("No active session for this class. Ask teacher to start attendance.");
      if (!attendanceCode) throw new Error("Enter attendance code.");
      if (!latitude || !longitude) throw new Error("Capture your location first.");

      const deviceInfo = {
        user_agent: navigator.userAgent,
        screen_size: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        ip_subnet: "web", // browser cannot access IP; placeholder
      };

      const payload = {
        attendance_session_id: activeSession.attendance_session_id,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        attendance_code: attendanceCode,
        device_info: deviceInfo,
      };

      const res = await fetch("/attendance/submit", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to submit attendance");

      setMsg("Attendance submitted successfully ✅");
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
          <Title order={2}>Student Dashboard</Title>
          <Text c="dimmed">Enroll and mark attendance</Text>
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
        <Title order={4}>Enroll in a class</Title>
        <Divider my="sm" />
        <Group align="flex-end" grow>
          <TextInput
            label="Class ID"
            placeholder="e.g., 1"
            value={enrollClassId}
            onChange={(e) => setEnrollClassId(e.target.value)}
          />
          <Button onClick={enroll} loading={loading}>
            Enroll
          </Button>
        </Group>
      </Paper>

      <Divider my="lg" />

      <Paper withBorder p="md" radius="md">
        <Group justify="space-between" mb="sm">
          <Title order={4}>Attendance</Title>
          <Badge color={activeSession ? "green" : "gray"}>
            {activeSession
              ? `Active Session #${activeSession.attendance_session_id}`
              : "No Active Session"}
          </Badge>
        </Group>

        <Select
          label="Select enrolled class"
          placeholder="Choose a class"
          data={classOptions}
          value={selectedClassId ? String(selectedClassId) : null}
          onChange={(val) => setSelectedClassId(val ? parseInt(val) : null)}
          searchable
        />

        <Group mt="md">
          <Button variant="light" onClick={() => checkActiveSession(selectedClassId)} disabled={!selectedClassId}>
            Refresh Active Session
          </Button>
        </Group>

        <Divider my="md" />

        <Card withBorder radius="md">
          <Title order={5}>Submit Attendance</Title>
          <Text c="dimmed" mb="sm">
            Enter the code, capture your location, then submit.
          </Text>

          <Stack>
            <TextInput
              label="Attendance code"
              placeholder="e.g., ABC123"
              value={attendanceCode}
              onChange={(e) => setAttendanceCode(e.target.value)}
            />

            <Group>
              <Button variant="light" onClick={getMyLocation}>
                Get My Location
              </Button>
              <Text c="dimmed">
                Lat: {latitude || "-"} | Lon: {longitude || "-"}
              </Text>
            </Group>

            <Button
              onClick={submitAttendance}
              disabled={!activeSession}
              loading={loading}
            >
              Submit Attendance
            </Button>
          </Stack>
        </Card>
      </Paper>

      <Divider my="lg" />

      <Paper withBorder p="md" radius="md">
        <Title order={4}>Your enrolled classes</Title>
        <Divider my="sm" />

        {classes.length === 0 ? (
          <Text c="dimmed">No enrolled classes yet.</Text>
        ) : (
          <Table striped highlightOnHover withTableBorder>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>ID</Table.Th>
                <Table.Th>Name</Table.Th>
                <Table.Th>Teacher ID</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {classes.map((c) => (
                <Table.Tr key={c.id}>
                  <Table.Td>{c.id}</Table.Td>
                  <Table.Td>{c.name}</Table.Td>
                  <Table.Td>{c.teacher_id}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Paper>
    </Container>
  );
}
