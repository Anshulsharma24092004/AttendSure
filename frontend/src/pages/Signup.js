import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Alert,
  Select,
  Group,
} from "@mantine/core";

export default function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");

  const [error, setError] = useState(null);
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(null);
    setMsg(null);
    setLoading(true);

    try {
      const res = await fetch("/auth/signup", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          password,
          role,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Signup failed");
        setLoading(false);
        return;
      }

      setMsg("Account created successfully. Please login.");
      setName("");
      setEmail("");
      setPassword("");
      setRole("student");

      // Redirect to login after short moment
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size={460} my={60}>
      <Title ta="center">Create your account</Title>
      <Text c="dimmed" ta="center" mt={5}>
        Sign up as a student or teacher
      </Text>

      <Paper withBorder shadow="md" p="lg" radius="md" mt="xl">
        {error && (
          <Alert color="red" title="Signup error" mb="md">
            {error}
          </Alert>
        )}
        {msg && (
          <Alert color="green" title="Success" mb="md">
            {msg}
          </Alert>
        )}

        <form onSubmit={handleSignup}>
          <TextInput
            label="Full name"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <TextInput
            label="Email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            mt="md"
          />

          <PasswordInput
            label="Password"
            placeholder="Choose a strong password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            mt="md"
          />

          <Select
            label="Role"
            data={[
              { value: "student", label: "Student" },
              { value: "teacher", label: "Teacher" },
            ]}
            value={role}
            onChange={(v) => setRole(v || "student")}
            required
            mt="md"
          />

          <Button type="submit" loading={loading} fullWidth mt="lg">
            Sign Up
          </Button>

          <Group justify="center" mt="md">
            <Text size="sm" c="dimmed">
              Already have an account?
            </Text>
            <Button variant="subtle" onClick={() => navigate("/login")}>
              Login
            </Button>
          </Group>
        </form>
      </Paper>
    </Container>
  );
}
