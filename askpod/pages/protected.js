// LANGUAGE: javascript
import { parseCookies } from "nookies";

export default function ProtectedPage({ user }) {
  return (
    <div>
      <h1>Protected Page</h1>
      <p>Welcome, {user.username}</p>
    </div>
  );
}

export async function getServerSideProps(context) {
  const { token } = parseCookies(context);
  if (!token) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }

  // Optionally validate the token via FastAPI endpoint
  const res = await fetch("http://localhost:8000/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status !== 200) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }
  const user = await res.json();
  return {
    props: { user },
  };
}