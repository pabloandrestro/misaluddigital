import { useState } from "react";
import {
  User,
  Shield,
  Lock,
  Bell,
  Calendar,
  ClipboardList,
  Moon,
  Smartphone,
  Laptop,
  Building2,
  Stethoscope,
  Briefcase,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/auth.store";
import { api } from "@/lib/api/client";

type TabId = "cuenta" | "seguridad" | "privacidad" | "notificaciones";

const TABS: { id: TabId; label: string; icon: typeof User }[] = [
  { id: "cuenta", label: "Cuenta", icon: User },
  { id: "seguridad", label: "Seguridad", icon: Shield },
  { id: "privacidad", label: "Privacidad", icon: Lock },
  { id: "notificaciones", label: "Notificaciones", icon: Bell },
];

// --- Datos de ejemplo (MOCK) ---------------------------------------------
// No existe backend todavia para sesiones activas, registro de actividad,
// terceros autorizados ni preferencias de notificacion. Se usan datos fijos
// para poder construir la UI; hay que reemplazarlos cuando el backend este listo.

const MOCK_SESSIONS = [
  { id: 1, device: "MacBook Pro - Chrome", location: "Santiago, Chile - Actual", current: true, icon: Laptop },
  { id: 2, device: "iPhone 15 Pro", location: "Santiago, Chile - Hace 2 horas", current: false, icon: Smartphone },
];

const MOCK_ACTIVITY = [
  { id: 1, label: "Inicio de sesión exitoso desde Chrome", when: "Hoy, 09:45" },
  { id: 2, label: "Cambio de contraseña realizado", when: "Hace 3 meses" },
];

const MOCK_THIRD_PARTIES = [
  { id: 1, name: "Red Salud Providencia", detail: "Acceso completo · Vence en 30 días", icon: Building2 },
  { id: 2, name: "Dr. Ricardo Salinas (Cardiología)", detail: "Acceso lectura · Permanente", icon: Stethoscope },
  { id: 3, name: "Clínica Alemana", detail: "Solo exámenes · Vence mañana", icon: Building2 },
];

interface NotificationRow {
  id: string;
  label: string;
  description: string;
  email: boolean;
  push: boolean;
}

const INITIAL_NOTIFICATIONS: NotificationRow[] = [
  { id: "citas", label: "Recordatorio de citas", description: "Avisos 24 horas antes de tu consulta programada.", email: true, push: true },
  { id: "cambios", label: "Cambios y cancelaciones", description: "Alertas inmediatas si tu médico reprograma una cita.", email: true, push: true },
  { id: "informes", label: "Nuevos informes disponibles", description: "Recibe un aviso cuando tus análisis estén listos.", email: true, push: false },
];

// --------------------------------------------------------------------------

export default function ConfiguracionPage() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser); // ajusta el nombre si tu store usa otro (ej. updateUser)
  const [activeTab, setActiveTab] = useState<TabId>("cuenta");

  // --- Cuenta ---
  const [name, setName] = useState(user?.name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");

  // --- Cambio de contraseña (in-page) ---
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>({});
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const handleSaveAccount = async () => {
    if (!name.trim()) {
      alert("El nombre no puede estar vacío.");
      return;
    }
    try {
      await api.patch(`/auth/account/settings/?email=${user?.email}`, { name });
      setUser({ ...user!, name });
      alert("Nombre actualizado correctamente.");
    } catch (err: any) {
      alert(err?.response?.data?.message ?? "Error al actualizar el nombre.");
    }
  };

  // Cambio de contraseña in-page: current_password + new_password + confirm_password
  const handleChangePassword = async () => {
    setPasswordErrors({});
    setPasswordSuccess(false);

    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordErrors({ general: "Completa los tres campos para cambiar la contraseña." });
      return;
    }

    setChangingPassword(true);
    try {
      await api.patch(`/auth/account/settings/?email=${user?.email}`, {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setPasswordSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      const errors = err?.response?.data?.errors;
      if (errors && typeof errors === "object") {
        // el backend devuelve errores por campo: current_password, new_password, confirm_password
        const flat: Record<string, string> = {};
        Object.entries(errors).forEach(([key, val]) => {
          flat[key] = Array.isArray(val) ? val[0] : String(val);
        });
        setPasswordErrors(flat);
      } else {
        setPasswordErrors({ general: err?.response?.data?.message ?? "No se pudo cambiar la contraseña." });
      }
    } finally {
      setChangingPassword(false);
    }
  };

  // --- Seguridad ---
  const handleConfigure2FA = () => {
    alert("La autenticación de dos pasos aún no está disponible.");
  };
  const handleCloseSession = (_id: number) => {
    alert("Cerrar sesiones remotas aún no está disponible (requiere backend).");
  };

  // --- Privacidad ---
  const [visibility, setVisibility] = useState<"solo_yo" | "medicos_autorizados">("medicos_autorizados");
  const [thirdParties, setThirdParties] = useState(MOCK_THIRD_PARTIES);
  const handleRevoke = (id: number) => {
    if (!confirm("¿Revocar el acceso de este tercero? (simulado, aún no conectado al backend)")) return;
    setThirdParties((prev) => prev.filter((t) => t.id !== id));
  };

  // --- Notificaciones ---
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const [silentMode, setSilentMode] = useState(false);
  const [silentFrom, setSilentFrom] = useState("22:00");
  const [silentTo, setSilentTo] = useState("07:00");

  const toggleNotification = (id: string, channel: "email" | "push") => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, [channel]: !n[channel] } : n))
    );
  };

  const handleSaveNotifications = () => {
    alert("Esta función estará disponible cuando exista el backend de preferencias de notificación.");
  };

  return (
    <div className="p-4 md:p-6">

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-semibold text-gray-900">Configuración</h1>
        <p className="text-sm text-gray-400 mt-1">Gestiona tu cuenta, privacidad y preferencias de seguridad.</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 items-start">

        {/* Mini navegación de pestañas */}
        <div className="w-full lg:w-64 flex-shrink-0 bg-white rounded-xl border border-gray-100 shadow-md p-2">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "bg-primary-light text-primary-mid"
                    : "text-gray-600 hover:bg-gray-50"
                }`}>
                <Icon size={18} strokeWidth={2} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Contenido */}
        <div className="flex-1 min-w-0 w-full">

          {/* --- CUENTA --- */}
          {activeTab === "cuenta" && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
              <h2 className="text-base font-semibold text-primary-mid mb-4 pb-4 border-b border-gray-100">
                Información de la Cuenta
              </h2>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-full bg-primary-mid flex items-center justify-center text-white text-xl font-semibold overflow-hidden flex-shrink-0">
                  {name?.[0] ?? "?"}
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-900">{name || "Usuario"}</p>
                  <p className="text-sm text-gray-400">Paciente</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Nombre completo</label>
                  <input value={name} onChange={(e) => setName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Correo electrónico</label>
                  <input value={email} onChange={(e) => setEmail(e.target.value)} disabled
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none bg-gray-50 text-gray-500" />
                </div>
              </div>

              {/* Cambio de contraseña in-page */}
              <div className="border border-gray-200 rounded-lg p-4 mb-6">
                <p className="text-sm font-medium text-gray-900 mb-1">Contraseña</p>
                <p className="text-xs text-gray-400 mb-4">Ingresa tu contraseña actual y la nueva contraseña.</p>

                <div className="grid grid-cols-1 gap-3 mb-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Contraseña actual</label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid"
                    />
                    {passwordErrors.current_password && (
                      <p className="text-xs text-red-500 mt-1">{passwordErrors.current_password}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Nueva contraseña</label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid"
                      />
                      {passwordErrors.new_password && (
                        <p className="text-xs text-red-500 mt-1">{passwordErrors.new_password}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Confirmar contraseña</label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-primary-mid"
                      />
                      {passwordErrors.confirm_password && (
                        <p className="text-xs text-red-500 mt-1">{passwordErrors.confirm_password}</p>
                      )}
                    </div>
                  </div>
                </div>

                {passwordErrors.general && (
                  <p className="text-xs text-red-500 mb-3">{passwordErrors.general}</p>
                )}
                {passwordSuccess && (
                  <p className="text-xs text-green-600 mb-3">Contraseña actualizada correctamente.</p>
                )}

                <button
                  onClick={handleChangePassword}
                  disabled={changingPassword}
                  className="px-4 py-2 rounded-full border border-primary-mid text-primary-mid text-sm hover:bg-primary-light transition-colors disabled:opacity-60">
                  {changingPassword ? "Cambiando..." : "Cambiar Contraseña"}
                </button>
              </div>

              <button
                onClick={handleSaveAccount}
                className="px-6 py-2.5 rounded-full bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors">
                Guardar Cambios
              </button>
            </div>
          )}

          {/* --- SEGURIDAD --- */}
          {activeTab === "seguridad" && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
              <h2 className="text-base font-semibold text-primary-mid mb-4 pb-4 border-b border-gray-100">
                Seguridad de la Cuenta
              </h2>

              <div className="bg-primary-light rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
                <div className="flex items-start gap-3">
                  <Smartphone size={20} className="text-primary-mid flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Autenticación de dos pasos</p>
                    <p className="text-xs text-gray-500">Añade una capa extra de seguridad mediante un código de verificación.</p>
                  </div>
                </div>
                <button
                  onClick={handleConfigure2FA}
                  className="px-4 py-2 rounded-full bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors flex-shrink-0">
                  Configurar
                </button>
              </div>

              <p className="text-sm font-medium text-gray-700 mb-2">Sesiones Activas</p>
              <div className="divide-y divide-gray-50 mb-6">
                {MOCK_SESSIONS.map((s) => {
                  const Icon = s.icon;
                  return (
                    <div key={s.id} className="flex items-center justify-between py-3">
                      <div className="flex items-center gap-3">
                        <Icon size={18} className="text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{s.device}</p>
                          <p className="text-xs text-gray-400">{s.location}</p>
                        </div>
                      </div>
                      {s.current ? (
                        <span className="px-3 py-1 bg-primary-light text-primary-mid text-xs rounded-full font-medium">En línea</span>
                      ) : (
                        <button onClick={() => handleCloseSession(s.id)} className="text-xs text-red-500 hover:underline">
                          Cerrar Sesión
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>

              <p className="text-sm font-medium text-gray-700 mb-2">Registro de Actividad</p>
              <div className="space-y-1 mb-6">
                {MOCK_ACTIVITY.map((a) => (
                  <div key={a.id} className="flex items-center justify-between text-sm">
                    <p className="text-gray-600">• {a.label}</p>
                    <p className="text-xs text-gray-400">{a.when}</p>
                  </div>
                ))}
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900 mb-1">Protección de Datos</p>
                <p className="text-xs text-gray-500">
                  Tus datos están protegidos por encriptación AES-256 y cumplen con los estándares HIPAA.
                </p>
              </div>
            </div>
          )}

          {/* --- PRIVACIDAD --- */}
          {activeTab === "privacidad" && (
            <div className="space-y-4">
              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
                <h2 className="text-base font-semibold text-primary-mid mb-1">Visibilidad del Perfil</h2>
                <p className="text-xs text-gray-400 mb-4">Controla quién puede ver tu información médica y perfil público</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button
                    onClick={() => setVisibility("solo_yo")}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border text-center transition-colors ${
                      visibility === "solo_yo" ? "border-primary-mid bg-primary-light" : "border-gray-200 hover:bg-gray-50"
                    }`}>
                    <Lock size={22} className="text-primary-mid" />
                    <p className="text-sm font-medium text-gray-900">Solo yo</p>
                    <p className="text-xs text-gray-400">Nadie puede ver tu perfil</p>
                  </button>
                  <button
                    onClick={() => setVisibility("medicos_autorizados")}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border text-center transition-colors ${
                      visibility === "medicos_autorizados" ? "border-primary-mid bg-primary-light" : "border-gray-200 hover:bg-gray-50"
                    }`}>
                    <Briefcase size={22} className="text-primary-mid" />
                    <p className="text-sm font-medium text-gray-900">Médicos autorizados</p>
                    <p className="text-xs text-gray-400">Solo profesionales con tu permiso.</p>
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
                <h2 className="text-base font-semibold text-primary-mid mb-1">Terceros autorizados</h2>
                <p className="text-xs text-gray-400 mb-4">Clínicas y doctores que actualmente tienen acceso a tus registros.</p>

                {thirdParties.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No hay terceros con acceso.</p>
                ) : (
                  <div className="divide-y divide-gray-50">
                    {thirdParties.map((t) => {
                      const Icon = t.icon;
                      return (
                        <div key={t.id} className="flex items-center justify-between py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0">
                              <Icon size={16} className="text-primary-mid" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">{t.name}</p>
                              <p className="text-xs text-gray-400">{t.detail}</p>
                            </div>
                          </div>
                          <button onClick={() => handleRevoke(t.id)} className="text-xs text-red-500 hover:underline flex-shrink-0">
                            Revocar acceso
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* --- NOTIFICACIONES --- */}
          {activeTab === "notificaciones" && (
            <div className="space-y-4">
              <div className="flex justify-end gap-6 text-xs text-gray-400 px-2">
                <span>Correo Electrónico</span>
                <span>Notificaciones</span>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Calendar size={18} className="text-primary-mid" />
                  <p className="text-sm font-semibold text-gray-900">Citas y Consultas</p>
                </div>
                <div className="divide-y divide-gray-50">
                  {notifications.filter((n) => n.id === "citas" || n.id === "cambios").map((n) => (
                    <div key={n.id} className="flex items-center justify-between py-3 gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900">{n.label}</p>
                        <p className="text-xs text-gray-400">{n.description}</p>
                      </div>
                      <div className="flex items-center gap-6 flex-shrink-0">
                        <ToggleSwitch checked={n.email} onChange={() => toggleNotification(n.id, "email")} />
                        <ToggleSwitch checked={n.push} onChange={() => toggleNotification(n.id, "push")} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
                <div className="flex items-center gap-2 mb-3">
                  <ClipboardList size={18} className="text-primary-mid" />
                  <p className="text-sm font-semibold text-gray-900">Resultados Médicos</p>
                </div>
                <div className="divide-y divide-gray-50">
                  {notifications.filter((n) => n.id === "informes").map((n) => (
                    <div key={n.id} className="flex items-center justify-between py-3 gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900">{n.label}</p>
                        <p className="text-xs text-gray-400">{n.description}</p>
                      </div>
                      <div className="flex items-center gap-6 flex-shrink-0">
                        <ToggleSwitch checked={n.email} onChange={() => toggleNotification(n.id, "email")} />
                        <ToggleSwitch checked={n.push} onChange={() => toggleNotification(n.id, "push")} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 md:p-6">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Moon size={18} className="text-primary-mid" />
                    <div>
                      <p className="text-sm font-semibold text-gray-900">Horario de Silencio</p>
                      <p className="text-xs text-gray-400">Suspender todas las notificaciones durante la noche.</p>
                    </div>
                  </div>
                  <ToggleSwitch checked={silentMode} onChange={() => setSilentMode((v) => !v)} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className={`rounded-lg p-3 ${silentMode ? "bg-gray-50" : "bg-gray-100 opacity-60"}`}>
                    <label className="block text-xs text-gray-400 mb-1">De las:</label>
                    <input type="time" value={silentFrom} disabled={!silentMode}
                      onChange={(e) => setSilentFrom(e.target.value)}
                      className="bg-transparent text-lg font-semibold text-gray-900 outline-none w-full" />
                  </div>
                  <div className={`rounded-lg p-3 ${silentMode ? "bg-gray-50" : "bg-gray-100 opacity-60"}`}>
                    <label className="block text-xs text-gray-400 mb-1">Hasta las:</label>
                    <input type="time" value={silentTo} disabled={!silentMode}
                      onChange={(e) => setSilentTo(e.target.value)}
                      className="bg-transparent text-lg font-semibold text-gray-900 outline-none w-full" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
                <p className="text-xs text-gray-400 text-center sm:text-left">
                  Tus cambios se guardarán automáticamente en todos tus dispositivos sincronizados.
                </p>
                <div className="flex gap-3 flex-shrink-0">
                  <button
                    onClick={() => setNotifications(INITIAL_NOTIFICATIONS)}
                    className="px-4 py-2 rounded-full border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                    Descartar
                  </button>
                  <button
                    onClick={handleSaveNotifications}
                    className="px-4 py-2 rounded-full bg-primary-mid text-white text-sm font-medium hover:bg-primary-dark transition-colors">
                    Guardar Cambios
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

// Switch simple reutilizable para las preferencias de notificacion
function ToggleSwitch({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      aria-pressed={checked}
      className={`w-11 h-6 rounded-full transition-colors relative flex-shrink-0 border ${
        checked ? "bg-primary-mid border-primary-mid" : "bg-gray-100 border-gray-300"
      }`}>
      <span
        className={`absolute left-0 top-0.5 w-5 h-5 rounded-full bg-white shadow-md ring-1 ring-black/5 transition-transform ${
          checked ? "translate-x-[22px]" : "translate-x-0.5"
        }`}
      />
    </button>
  );
}
