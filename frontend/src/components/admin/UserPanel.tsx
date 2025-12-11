import { useEffect, useState } from "react";
import { getUsers, createUser, updateUser, deleteUser } from "../../api/api_users";
import { motion } from "framer-motion";
import type { User } from "../../types/User";


export default function UsersPanel() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    address: "",
    channel: "web",
  });

  async function load() {
    setLoading(true);
    const data = await getUsers();
    setUsers(data || []);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  function openCreate() {
    setEditing(null);
    setForm({
      name: "",
      email: "",
      phone: "",
      address: "",
      channel: "web",
    });
    setShowForm(true);
  }

  function openEdit(user: User) {
    setEditing(user);
    setForm({
      name: user.name || "",
      email: user.email || "",
      phone: user.phone || "",
      address: user.address || "",
      channel: user.channel || "web",
    });
    setShowForm(true);
  }

  async function submit() {
    if (editing) {
      await updateUser(editing.id, form);
    } else {
      await createUser(form);
    }
    setShowForm(false);
    load();
  }

  async function remove(id: number) {
    if (!confirm("¿Seguro que deseas eliminar este usuario?")) return;
    await deleteUser(id);
    load();
  }

  return (
    <div className="p-6">

      {/* TOP BAR */}
      <div className="flex justify-between items-center mb-5">
        <h3 className="text-xl font-semibold text-text-primary">
          Usuarios registrados
        </h3>

        <button
          onClick={openCreate}
          className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition"
        >
          + Crear Usuario
        </button>
      </div>

      {/* TABLE */}
      {loading ? (
        <p className="text-text-secondary">Cargando usuarios...</p>
      ) : users.length === 0 ? (
        <p className="text-text-secondary text-sm">No hay usuarios registrados.</p>
      ) : (
        <motion.table
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="w-full bg-surface border border-border rounded-xl overflow-hidden"
        >
          <thead className="bg-surface/70 border-b border-border text-left">
            <tr>
              <th className="p-3 text-text-secondary text-sm">ID</th>
              <th className="p-3 text-text-secondary text-sm">Nombre</th>
              <th className="p-3 text-text-secondary text-sm">Email</th>
              <th className="p-3 text-text-secondary text-sm">Teléfono</th>
              <th className="p-3 text-text-secondary text-sm">Canal</th>
              <th className="p-3"></th>
            </tr>
          </thead>

          <tbody>
            {users.map((u) => (
              <tr
                key={u.id}
                className="border-b border-border hover:bg-surface/50 transition"
              >
                <td className="p-3">{u.id}</td>
                <td className="p-3">{u.name}</td>
                <td className="p-3">{u.email}</td>
                <td className="p-3">{u.phone}</td>
                <td className="p-3">{u.channel}</td>

                <td className="p-3 text-right space-x-2">
                  <button
                    onClick={() => openEdit(u)}
                    className="px-3 py-1 bg-primary/20 text-primary rounded-md hover:bg-primary/30"
                  >
                    Editar
                  </button>

                  <button
                    onClick={() => remove(u.id)}
                    className="px-3 py-1 bg-red-500/20 text-red-500 rounded-md hover:bg-red-500/30"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </motion.table>
      )}

      {/* MODAL FORM */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
        >
          <div className="bg-surface p-6 rounded-xl border border-border shadow-xl w-96">
            <h4 className="text-lg font-semibold mb-4">
              {editing ? "Editar Usuario" : "Crear Usuario"}
            </h4>

            {/* FORM */}
            <div className="space-y-3">
              {["name", "email", "phone", "address"].map((field) => (
                <div key={field}>
                  <label className="text-sm text-text-secondary capitalize">
                    {field}
                  </label>
                  <input
                    className="w-full px-3 py-2 mt-1 bg-background border border-border rounded-lg"
                    value={(form as any)[field]}
                    onChange={(e) =>
                      setForm({ ...form, [field]: e.target.value })
                    }
                  />
                </div>
              ))}

              {/* SELECT */}
              <div>
                <label className="text-sm text-text-secondary">Canal</label>
                <select
                  className="w-full px-3 py-2 mt-1 bg-background border border-border rounded-lg"
                  value={form.channel}
                  onChange={(e) =>
                    setForm({ ...form, channel: e.target.value })
                  }
                >
                  <option value="web">Web</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
              </div>
            </div>

            {/* BUTTONS */}
            <div className="flex justify-end mt-5 space-x-2">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-surface border border-border rounded-lg hover:bg-surface/70"
              >
                Cancelar
              </button>

              <button
                onClick={submit}
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
              >
                Guardar
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}