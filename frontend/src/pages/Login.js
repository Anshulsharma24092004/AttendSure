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
  Group,
  Alert,
} from "@mantine/core";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Login failed");
        setLoading(false);
        return;
      }

      const meRes = await fetch("/auth/me", {
        method: "GET",
        credentials: "include",
      });
      const meData = await meRes.json();

      if (!meRes.ok) {
        setError(meData.error || "Failed to fetch user");
        setLoading(false);
        return;
      }

      if (meData.role === "teacher") navigate("/teacher");
      else navigate("/student");
    } catch (err) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size={420} my={60}>
      <Title ta="center">AttendSure</Title>
      <Text c="dimmed" ta="center" mt={5}>
        Login to continue
      </Text>

      <Paper withBorder shadow="md" p="lg" radius="md" mt="xl">
        {error && (
          <Alert color="red" mb="md" title="Login error">
            {error}
          </Alert>
        )}

        <form onSubmit={handleLogin}>
          <TextInput
            label="Email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <PasswordInput
            label="Password"
            placeholder="Your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            mt="md"
          />

          <Group justify="space-between" mt="lg">
            <Button type="submit" loading={loading} fullWidth>
              Login
            </Button>
          </Group>
        </form>
      </Paper>
      <Group justify="center" mt="md">
        <Text size="sm" c="dimmed">
          Don't have an account?
        </Text>
        <Button variant="subtle" onClick={() => navigate("/signup")}>
          Sign up
        </Button>
      </Group>
    </Container>
  );
}
