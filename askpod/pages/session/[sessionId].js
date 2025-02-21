import Navbar from "../../components/Navbar";
import Sidebar from "../../components/Sidebar";
import RightSidebar from "../../components/RightSidebar";
import Chat from "../../components/Chat";
import { parseCookies } from "nookies";

export default function SessionHome({ user, sessionId }) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar user={user} />
      <div className="flex flex-1">
        {/* Left Sidebar: List sessions */}
        <aside className="w-80 bg-white border-r p-4 flex flex-col">
          <Sidebar />
        </aside>
        {/* Middle Content: Chat interface */}
        <main className="flex-1 p-4 flex flex-col">
          <div className="flex-1">
            <Chat currentSessionId={sessionId} />
          </div>
        </main>
        {/* Right Sidebar: Controls only for current session */}
        <aside className="w-80 bg-white border-l p-4 flex flex-col justify-end">
  <RightSidebar key={sessionId} currentSessionId={parseInt(sessionId, 10)} />
</aside>
      </div>
    </div>
  );
}

export async function getServerSideProps(context) {
  const { token } = parseCookies(context);
  const { sessionId } = context.params;

  // Redirect to login if token is missing
  if (!token) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }

  // Validate token via FastAPI
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
    props: {
      user,
      sessionId,
    },
  };
}