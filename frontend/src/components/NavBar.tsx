interface Props {
  page: string;
  setPage: (p: string) => void;
}

export default function NavBar({ page, setPage }: Props) {
  return (
    <nav className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-md bg-linear-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-white font-bold">AC</div>
        <div>
          <div className="font-semibold">Asistente Comercial</div>
          <div className="text-xs text-slate-500">Vendedor de teclados mecánicos — Español (Col)</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={() => setPage("chat")}
          className={`px-3 py-1 rounded-md ${page === "chat" ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-50"}`}
        >Chat</button>

        <button
          onClick={() => setPage("admin")}
          className={`px-3 py-1 rounded-md ${page === "admin" ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-50"}`}
        >Admin</button>
      </div>
    </nav>
  );
}