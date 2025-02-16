import { useEffect } from "react";
import { useRouter } from "next/router";
import nookies from "nookies";

export default function Logout() {
  const router = useRouter();

  useEffect(() => {
    // Clear user session or token here
    nookies.destroy(null, "token");

    // Redirect to the login page or home page
    router.push("/login");
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <p>Logging out...</p>
    </div>
  );
}