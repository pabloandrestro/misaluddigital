import { useEffect, useRef, useState } from "react";
import {
  Sparkles,
  Send,
  Paperclip,
  Lightbulb,
  ShieldCheck,
  Lock,
  FileText,
  Pill,
  Activity,
  CalendarClock,
  ClipboardList,
  RefreshCcw,
  FileDown,
  History,
  MessageCircleQuestion,
  CheckCircle2,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/auth.store";
import robotImg from "@/assets/img/robot.png";

interface Message {
  id: string;
  from: "bot" | "user";
  text: string;
  time: string;
}

// --- MOCK ------------------------------------------------------------
// El backend de ai_analysis (Sprint 2-4) todavia no tiene endpoints de chat,
// solo un modelo AIRecommendation sin relacion con conversaciones. Todo lo
// de esta pantalla es simulado hasta que exista el servicio real.

const nowLabel = () =>
  new Date().toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" });

const SUGGESTIONS = [
  { label: "¿Qué significa este examen?", icon: FileText },
  { label: "Explícame mi receta", icon: Pill },
  { label: "Resume mi historial", icon: ClipboardList },
  { label: "¿Cuándo fue mi último control?", icon: CalendarClock },
  { label: "Tengo dolor de cabeza, ¿qué debo observar?", icon: Activity },
];

const TOPICS = [
  { label: "Resultados de exámenes", icon: FileText },
  { label: "Medicamentos", icon: Pill },
  { label: "Síntomas generales", icon: Activity },
  { label: "Próximos controles", icon: CalendarClock },
  { label: "Resumen de tu historial", icon: ClipboardList },
];

// Respuestas simuladas segun palabras clave del mensaje del usuario
function getMockReply(userText: string): string {
  const text = userText.toLowerCase();

  if (text.includes("hemograma") || text.includes("examen") || text.includes("resultado")) {
    return "He revisado tu hemograma del 12 de octubre de 2024.\n\nEn términos generales, tus resultados están dentro de los rangos normales.\n\n¿Te gustaría que te explique algún valor en particular?";
  }
  if (text.includes("receta") || text.includes("medicament")) {
    return "Puedo ayudarte a entender tu receta o medicamentos actuales. Cuéntame el nombre del medicamento o sube la receta desde \"Mis documentos\" para que la revise.";
  }
  if (text.includes("historial") || text.includes("resum")) {
    return "Aquí tienes un resumen general de tu historial médico: cuentas con documentos, condiciones y medicamentos registrados en tu perfil. ¿Quieres que me enfoque en algo específico, como alergias o condiciones crónicas?";
  }
  if (text.includes("control") || text.includes("cita")) {
    return "Por ahora no tengo acceso a tu calendario de citas médicas. Puedes revisar tus documentos más recientes en el Panel principal mientras conectamos esta función.";
  }
  if (text.includes("dolor") || text.includes("síntoma") || text.includes("sintoma")) {
    return "Gracias por contarme. Recuerda que no puedo reemplazar una evaluación médica profesional. Si el síntoma es intenso, repentino o empeora, te recomiendo acudir a un centro de salud o contactar a tu médico.";
  }
  return "Gracias por tu consulta. Esta es una respuesta de ejemplo mientras se conecta el asistente real — pronto podré responder según tus documentos y perfil médico.";
}

export default function AiInsightsPage() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.name?.split(" ")[0] ?? "";

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      from: "bot",
      text: `¡Hola${firstName ? " " + firstName : ""}! 👋\nSoy tu asistente de salud.\n\nPuedo ayudarte a entender mejor tus documentos médicos, organizar información de tu historial y resolver dudas generales.\n\n¿Qué necesitas revisar hoy?`,
      time: nowLabel(),
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    const userMsg: Message = { id: crypto.randomUUID(), from: "user", text: trimmed, time: nowLabel() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setTyping(true);

    // Simula tiempo de respuesta del asistente
    setTimeout(() => {
      const botMsg: Message = {
        id: crypto.randomUUID(),
        from: "bot",
        text: getMockReply(trimmed),
        time: nowLabel(),
      };
      setMessages((prev) => [...prev, botMsg]);
      setTyping(false);
    }, 900);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="p-4 md:p-6">

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-semibold text-gray-900 flex items-center gap-2">
          Chatea con la IA <Sparkles size={18} className="text-primary-mid" />
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Consulta dudas generales sobre tus documentos, recetas o exámenes.
          <br className="hidden sm:block" />
          La IA te orienta, pero no reemplaza una atención médica profesional.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 items-start">

        {/* COLUMNA CHAT */}
        <div className="flex-1 min-w-0 w-full bg-white rounded-xl border border-gray-100 shadow-md flex flex-col" style={{ height: "70vh" }}>

          {/* Header del asistente */}
          <div className="flex items-center gap-3 p-4 border-b border-gray-100 flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0 overflow-hidden">
              <img src={robotImg} alt="Asistente" className="w-8 h-8 object-contain" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">Asistente de salud</p>
              <p className="text-xs text-green-500 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> En línea
              </p>
            </div>
          </div>

          {/* Mensajes */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.from === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] sm:max-w-[70%] ${m.from === "bot" ? "flex gap-2" : ""}`}>
                  {m.from === "bot" && (
                    <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0 mt-1 overflow-hidden">
                      <img src={robotImg} alt="Asistente" className="w-5 h-5 object-contain" />
                    </div>
                  )}
                  <div
                    className={`rounded-xl px-4 py-3 text-sm whitespace-pre-line ${
                      m.from === "bot"
                        ? "bg-primary-light text-gray-700"
                        : "bg-primary-mid text-white"
                    }`}>
                    {m.text}
                    <p className={`text-[10px] mt-1.5 ${m.from === "bot" ? "text-gray-400" : "text-white/70"} flex items-center gap-1 justify-end`}>
                      {m.time}
                      {m.from === "user" && <CheckCircle2 size={10} />}
                    </p>
                  </div>
                </div>
              </div>
            ))}

            {typing && (
              <div className="flex justify-start">
                <div className="flex gap-2">
                  <div className="w-7 h-7 rounded-full bg-primary-light flex items-center justify-center flex-shrink-0 overflow-hidden">
                    <img src={robotImg} alt="Asistente" className="w-5 h-5 object-contain" />
                  </div>
                  <div className="bg-gray-50 rounded-xl px-4 py-3 text-sm text-gray-400">
                    Escribiendo...
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sugerencias rápidas */}
          <div className="px-4 pb-3 flex-shrink-0">
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => {
                const Icon = s.icon;
                return (
                  <button
                    key={s.label}
                    onClick={() => sendMessage(s.label)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-primary-mid/40 text-primary-mid text-xs hover:bg-primary-light transition-colors">
                    <Icon size={13} />
                    {s.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-gray-100 flex-shrink-0">
            <div className="flex items-center gap-2 bg-gray-50 rounded-full px-2 py-1.5">
              <button type="button" className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 flex-shrink-0">
                <Paperclip size={16} />
              </button>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Escribe tu consulta médica..."
                className="flex-1 min-w-0 bg-transparent outline-none text-sm text-gray-700 placeholder-gray-400"
              />
              <button
                type="submit"
                disabled={!input.trim()}
                className="w-9 h-9 rounded-full bg-primary-mid text-white flex items-center justify-center hover:bg-primary-dark transition-colors disabled:opacity-40 flex-shrink-0">
                <Send size={15} />
              </button>
            </div>
            <p className="text-[11px] text-gray-400 mt-2 flex items-center gap-1">
              <Lock size={10} />
              La información entregada por la IA es orientativa y no reemplaza una evaluación médica profesional.
            </p>
          </form>
        </div>

        {/* COLUMNA DERECHA */}
        <div className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-4">

          {/* Puedes preguntarme sobre */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb size={16} className="text-yellow-400" />
              <p className="text-sm font-medium text-gray-700">Puedes preguntarme sobre:</p>
            </div>
            <div className="space-y-2">
              {TOPICS.map((t) => {
                const Icon = t.icon;
                return (
                  <button
                    key={t.label}
                    onClick={() => sendMessage(t.label)}
                    className="w-full flex items-center gap-2 text-sm text-gray-600 hover:text-primary-mid transition-colors text-left">
                    <Icon size={14} className="text-primary-mid flex-shrink-0" />
                    {t.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Importante */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck size={16} className="text-primary-mid" />
              <p className="text-sm font-medium text-gray-700">Importante</p>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed mb-3">
              La información entregada por la IA es orientativa y no reemplaza una evaluación médica profesional.
              Ante síntomas graves, acude a urgencias o contacta a tu médico.
            </p>
            <div className="flex justify-center">
              <img src={robotImg} alt="Robot IA" className="w-20 h-20 object-contain" />
            </div>
          </div>

          {/* Privacidad y seguridad */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <Lock size={16} className="text-primary-mid" />
              <p className="text-sm font-medium text-gray-700">Privacidad y seguridad</p>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed mb-2">
              Tus conversaciones están protegidas bajo estándares de seguridad médica y encriptación de datos.
            </p>
            <p className="text-xs text-green-600 flex items-center gap-1 font-medium">
              <CheckCircle2 size={13} /> Datos 100% protegidos
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
