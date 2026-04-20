import Navbar from "../components/Navbar";

export default function AppLayout({ children , onLogout}) {
  return (
    <div className="bg-bg text-fg min-h-screen">
      <Navbar onLogout={onLogout}/>
      <main className="p-6">
        {children}
      </main>
    </div>
  );
}
