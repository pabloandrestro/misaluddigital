import { useState } from "react";
import { useNavigate } from "react-router-dom";
import loginIllustration from "@/assets/img/login-illustration.png";
import logoSaludaldia from "@/assets/logo/logo-saludaldia.png";
import textoSaludaldia from "@/assets/logo/texto.png";

export default function CompleteProfilePage() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);

    return (
        <div className="min-h-screen bg-white px-4 py-4 md:py-6">
            <section className="mx-auto flex min-h-[calc(100vh-32px)] w-full max-w-5xl items-center rounded-[32px] border border-rose-100 bg-[#f7f7f7] p-4 md:min-h-[calc(100vh-48px)] md:p-6 lg:p-7">
                <div className="grid w-full gap-8 lg:grid-cols-2">
                    <div className="hidden h-full flex-col pt-6 lg:flex">
                        <div className="mb-8 flex items-center gap-3">
                            <img
                                src={logoSaludaldia}
                                alt="Logo Saludaldia"
                                className="h-12 w-auto object-contain"
                            />
                            <img
                                src={textoSaludaldia}
                                alt="Saludaldia"
                                className="h-8 w-auto object-contain"
                            />
                        </div>

                        <h2 className="max-w-sm text-4xl font-bold leading-tight text-gray-800">
                            Tu historial médico siempre contigo
                        </h2>

                        <p className="mt-3 max-w-xs text-base font-semibold leading-snug text-gray-500">
                            Guarda, organiza y comparte tus documentos médicos de forma segura.
                        </p>

                        <div className="my-6 flex justify-center">
                            <img
                                src={loginIllustration}
                                alt="Historial médico digital"
                                className="w-full max-w-[300px] object-contain"
                            />
                        </div>

                        <div className="flex items-center gap-3 text-sm font-semibold text-gray-600">
                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--brand-dark)] text-white">
                                ✓
                            </div>
                            <span>Seguro</span>
                            <span>•</span>
                            <span>Privado</span>
                            <span>•</span>
                            <span>Confiable</span>
                        </div>
                    </div>

                    <div className="mx-auto w-full max-w-[480px] rounded-[32px] bg-white px-6 py-6 shadow-sm md:px-8">
                        <div className="text-center">
                            <h1 className="text-2xl font-bold text-gray-950">
                                Completa tu perfil médico
                            </h1>
                            <p className="mt-1 text-sm text-gray-500">
                                Esto nos ayuda a cuidarte mejor
                            </p>
                        </div>

                        <div className="my-5 flex items-center justify-center gap-4">
                            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--brand-dark)] text-sm font-semibold text-white">
                                1
                            </div>

                            <div className="h-[2px] w-16 bg-[var(--brand-dark)]" />

                            <div
                                className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold ${step === 2
                                    ? "bg-[var(--brand-dark)] text-white"
                                    : "bg-gray-100 text-gray-400"
                                    }`}
                            >
                                2
                            </div>
                        </div>

                        {step === 1 ? (
                            <div className="rounded-[24px] border border-gray-200 p-5">
                                <h2 className="font-semibold text-gray-900">
                                    Información básica
                                </h2>

                                <p className="mt-1 text-sm text-gray-500">
                                    Cuéntanos algunos datos sobre ti
                                </p>

                                <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Fecha de nacimiento
                                        </label>
                                        <input
                                            type="date"
                                            className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                                        />
                                    </div>

                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Sexo
                                        </label>
                                        <select className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]">
                                            <option>Selecciona</option>
                                            <option>Masculino</option>
                                            <option>Femenino</option>
                                            <option>Otro</option>
                                            <option>Prefiero no decir</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Grupo sanguíneo
                                        </label>
                                        <select className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]">
                                            <option>Selecciona</option>
                                            <option>O+</option>
                                            <option>O-</option>
                                            <option>A+</option>
                                            <option>A-</option>
                                            <option>B+</option>
                                            <option>B-</option>
                                            <option>AB+</option>
                                            <option>AB-</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Peso
                                        </label>
                                        <input
                                            type="number"
                                            placeholder="Kg"
                                            className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                                        />
                                    </div>
                                </div>

                                <div className="mt-4 rounded-lg bg-[var(--brand-light)] p-3 text-sm text-gray-600">
                                    Puedes completar más información más tarde desde tu perfil.
                                </div>

                                <button
                                    onClick={() => setStep(2)}
                                    className="mt-5 w-full rounded-lg bg-[var(--brand-dark)] py-3 font-medium text-white transition hover:bg-[var(--brand-mid)]"
                                >
                                    Continuar
                                </button>

                                <button
                                    onClick={() => navigate("/")}
                                    className="mt-3 w-full text-center text-sm text-[var(--brand-dark)] hover:underline"
                                >
                                    Saltar por ahora
                                </button>
                            </div>
                        ) : (
                            <div className="rounded-[24px] border border-gray-200 p-5">
                                <h2 className="font-semibold text-gray-900">
                                    Información médica
                                </h2>

                                <p className="mt-1 text-sm text-gray-500">
                                    Cuéntanos algunos datos sobre tu salud
                                </p>

                                <div className="mt-4 space-y-3">
                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Alergias conocidas
                                        </label>
                                        <select className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]">
                                            <option>Ninguna</option>
                                            <option>Medicamentos</option>
                                            <option>Alimentos</option>
                                            <option>Otra</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="mb-2 block text-sm font-medium text-gray-800">
                                            Enfermedades crónicas
                                        </label>

                                        <div className="grid grid-cols-2 gap-2">
                                            {["Diabetes", "Hipertensión", "Asma", "Hipotiroidismo"].map(
                                                (item) => (
                                                    <label
                                                        key={item}
                                                        className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-800"
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            className="h-4 w-4 rounded border-gray-300 text-[var(--brand-dark)] focus:ring-[var(--brand-mid)]"
                                                        />
                                                        {item}
                                                    </label>
                                                )
                                            )}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Otra enfermedad
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="Escribe la enfermedad"
                                            className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                                        />
                                    </div>

                                    <div>
                                        <label className="mb-1 block text-sm font-medium text-gray-800">
                                            Medicamentos permanentes
                                        </label>
                                        <input
                                            type="text"
                                            placeholder="Ej: Losartán 50mg, Levotiroxina 100mg"
                                            className="w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm outline-none transition focus:border-[var(--brand-mid)] focus:ring-2 focus:ring-[var(--brand-subtle)]"
                                        />
                                        <p className="mt-1 text-xs text-gray-500">
                                            Escribe los medicamentos que tomas de forma regular.
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-3 rounded-lg bg-[var(--brand-light)] p-3 text-sm text-gray-600">
                                    Esta información puede modificarse posteriormente.
                                </div>

                                <div className="mt-5 flex items-center justify-between gap-3">
                                    <button
                                        onClick={() => setStep(1)}
                                        className="w-full rounded-lg border border-[var(--brand-mid)] py-2.5 font-medium text-[var(--brand-dark)] transition hover:bg-[var(--brand-light)]"
                                    >
                                        Volver
                                    </button>

                                    <button
                                        onClick={() => navigate("/")}
                                        className="w-full rounded-lg bg-[var(--brand-dark)] py-2.5 font-medium text-white transition hover:bg-[var(--brand-mid)]"
                                    >
                                        Finalizar perfil
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
}