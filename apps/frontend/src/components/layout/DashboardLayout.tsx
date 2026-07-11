import { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/lib/store/auth.store";
import { UserCircle, LayoutDashboard, FolderOpen, User, Bot, Settings, LogOut, Bell, HelpCircle, Search, Menu, X } from "lucide-react";
import logoWhite from "@/assets/img/logo-white.png";

const NAV = [
  { path: "/",            label: "Panel principal", icon: LayoutDashboard },
  { path: "/documents",   label: "Mis documentos",  icon: FolderOpen },
  { path: "/profile",     label: "Perfil médico",   icon: User },
  { path: "/ai-insights", label: "Asistente IA",    icon: Bot },
  { path: "/settings",    label: "Configuración",   icon: Settings },
];

const FOOTER_LINKS = ["Privacidad", "Términos de Uso", "Contacto", "Ayuda"];

export default function DashboardLayout() {
  const user     = useAuthStore((s) => s.user);
  const logout   = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50">

      {/* OVERLAY MÓVIL */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR */}
      <aside
        className={`w-52 flex flex-col flex-shrink-0 min-h-screen fixed md:static z-50 transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{ background: "linear-gradient(to bottom, var(--color-primary-dark), var(--color-primary-mid))" }}
      >

        {/* Logo + botón cerrar (móvil) */}
        <div className="p-4 border-b border-primary-mid flex flex-col items-center gap-1 relative">
          <button
            onClick={() => setSidebarOpen(false)}
            className="absolute top-3 right-3 text-white md:hidden"
          >
            <X size={18} />
          </button>
          <img src={logoWhite} alt="Saludaldia" className="w-20 h-16 object-contain" />
          <p className="text-primary-text text-[10px] uppercase tracking-wide text-center">
            Historial médico digital
          </p>
        </div>

        {/* Navegación */}
        <nav className="flex-1 p-2 space-y-0.5">
          {NAV.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={label}
              to={path}
              end={path === "/"}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-primary-mid text-white font-medium"
                    : "text-primary-subtle hover:bg-primary-mid"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Usuario */}
        <div className="p-3 border-t border-primary-mid flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary-mid flex items-center justify-center text-primary-subtle flex-shrink-0">
            <UserCircle size={20} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-xs font-medium truncate">
              {user?.name}
            </p>
            {user?.rut && (
              <p className="text-primary-text text-[10px]">RUT {user.rut}</p>
            )}
          </div>
        </div>

        {/* Cerrar sesión */}
        <div className="p-2 border-t border-primary-mid">
          <button
            onClick={() => { logout(); navigate("/login"); }}
            className="w-full px-3 py-2 text-sm text-primary-subtle hover:bg-primary-mid rounded-lg text-left transition-colors flex items-center gap-2"
          >
            <LogOut size={16} />
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* COLUMNA DERECHA */}
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">

        {/* HEADER */}
        <header className="h-14 bg-white border-b border-gray-100 flex items-center px-3 md:px-5 gap-2 md:gap-3 flex-shrink-0">

          {/* Botón hamburguesa (solo móvil) */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden w-8 h-8 flex items-center justify-center text-gray-600 flex-shrink-0"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2 bg-gray-100 rounded-full px-3 md:px-4 py-2 flex-1 max-w-lg min-w-0">
            <Search size={14} className="text-gray-400 flex-shrink-0" />
            <input
              type="text"
              placeholder="Buscar..."
              className="bg-transparent outline-none text-sm text-gray-700 placeholder-gray-400 w-full min-w-0"
            />
          </div>
          <div className="ml-auto flex gap-2 flex-shrink-0">
            <button className="w-8 h-8 rounded-full border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-50">
              <Bell size={15} />
            </button>
            <button className="w-8 h-8 rounded-full border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-50">
              <HelpCircle size={15} />
            </button>
          </div>
        </header>

        {/* CONTENIDO */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>

        {/* FOOTER */}
        <footer className="bg-white border-t border-gray-100 px-3 md:px-5 py-3 flex flex-col md:flex-row items-center gap-2 md:gap-4 flex-shrink-0 text-center md:text-left">
          <span className="text-primary-mid text-xs font-semibold">Saludaldia</span>
          <span className="text-gray-400 text-xs">© 2026 Saludaldia — Seguridad de Datos Protegida</span>
          <div className="flex gap-4 md:ml-auto flex-wrap justify-center">
            {FOOTER_LINKS.map((link) => (
              <a key={link} href="#" className="text-gray-500 text-xs hover:text-primary-mid transition-colors">
                {link}
              </a>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}
