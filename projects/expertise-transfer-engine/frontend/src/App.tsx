import { useState, useRef } from "react";

// ---- Types ----
type Step = "record" | "interview" | "spec";

interface Question {
  id: string;
  text: string;
  category: string;
}

interface SpecSection {
  title: string;
  content: string;
}

// ---- API Client ----
const API_BASE = "http://127.0.0.1:8010";
const API = API_BASE;

async function uploadAudio(blob: Blob) {
  const form = new FormData();
  form.append("file", blob, "recording.webm");
  const res = await fetch(`${API}/record`, { method: "POST", body: form });
  return res.json() as Promise<{ session_id: string; transcript: string }>;
}

async function getQuestions(sessionId: string) {
  const res = await fetch(`${API}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return res.json() as Promise<{
    questions: Question[];
    total_rounds: number;
    current_round: number;
  }>;
}

async function submitAnswer(
  sessionId: string,
  questionId: string,
  answer: string
) {
  const res = await fetch(`${API}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question_id: questionId, answer }),
  });
  return res.json() as Promise<{
    next_question: Question | null;
    all_answered: boolean;
    current_round: number;
  }>;
}

async function getSpec(sessionId: string) {
  const res = await fetch(`${API}/spec/${sessionId}`);
  return res.json() as Promise<{
    session_id: string;
    sections: SpecSection[];
    raw_markdown: string;
  }>;
}

// ---- Components ----

function RecordStep({
  onDone,
}: {
  onDone: (sessionId: string, transcript: string) => void;
}) {
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setUploading(true);
        try {
          const data = await uploadAudio(blob);
          setTranscript(data.transcript);
          setSessionId(data.session_id);
        } catch (e) {
          setError("Erreur lors de l'envoi. Vérifie que le backend tourne.");
        }
        setUploading(false);
      };

      mediaRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setError("Microphone non accessible. Autorise-le dans ton navigateur.");
    }
  };

  const stopRecording = () => {
    mediaRef.current?.stop();
    setRecording(false);
  };

  return (
    <div className="max-w-xl mx-auto text-center space-y-6">
      <h1 className="text-3xl font-bold text-white">
        Expertise Transfer Engine
      </h1>
      <p className="text-gray-400">
        Parle de ton expertise. L'IA va t'interviewer pour capturer ta vraie
        compétence.
      </p>

      <div className="flex justify-center gap-4">
        {!recording ? (
          <button
            onClick={startRecording}
            disabled={uploading}
            className="px-8 py-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-lg font-semibold disabled:opacity-50 transition"
          >
            {uploading ? "Envoi en cours..." : "🎤  Enregistrer"}
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-full text-lg font-semibold animate-pulse transition"
          >
            ⏹  Arrêter
          </button>
        )}
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {transcript && (
        <div className="bg-gray-800 rounded-xl p-6 text-left space-y-4">
          <h2 className="text-lg font-semibold text-green-400">
            ✅ Transcription
          </h2>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
            {transcript}
          </p>
          <button
            onClick={() => sessionId && onDone(sessionId, transcript)}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold transition"
          >
            Continuer → Questions
          </button>
        </div>
      )}
    </div>
  );
}

function InterviewStep({
  sessionId,
  onDone,
}: {
  sessionId: string;
  onDone: () => void;
}) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQ, setCurrentQ] = useState<Question | null>(null);
  const [round, setRound] = useState(1);
  const [answered, setAnswered] = useState(0);
  const [total, setTotal] = useState(1);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [done, setDone] = useState(false);
  const [qaLog, setQaLog] = useState<
    { question: string; answer: string }[]
  >([]);

  const start = async () => {
    setLoading(true);
    try {
      const data = await getQuestions(sessionId);
      setQuestions(data.questions);
      setCurrentQ(data.questions[0] || null);
      setTotal(data.total_rounds);
    } catch {
      setQuestions([]);
    }
    setLoading(false);
  };

  // Auto-start
  useState(() => {
    start();
  });

  const handleAnswer = async () => {
    if (!currentQ || !answer.trim()) return;

    setQaLog((prev) => [
      ...prev,
      { question: currentQ.text, answer: answer.trim() },
    ]);
    setAnswered((a) => a + 1);
    setAnswer("");

    try {
      const data = await submitAnswer(sessionId, currentQ.id, answer.trim());
      if (data.all_answered) {
        setDone(true);
      } else if (data.next_question) {
        setCurrentQ(data.next_question);
        setRound(data.current_round);
      } else {
        setDone(true);
      }
    } catch {
      setDone(true);
    }
  };

  if (loading) {
    return (
      <div className="text-center text-gray-400 py-20">
        Génération des questions...
      </div>
    );
  }

  if (done) {
    return (
      <div className="max-w-xl mx-auto text-center space-y-6">
        <h2 className="text-3xl font-bold text-green-400">✅ Interview terminée !</h2>
        <p className="text-gray-400">
          {answered} questions répondues. Génération du spec...
        </p>
        <button
          onClick={onDone}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold transition"
        >
          Voir le Spec →
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex justify-between text-sm text-gray-500">
        <span>Tour {round}/{total}</span>
        <span>Questions répondues : {answered}</span>
      </div>

      {currentQ && (
        <div className="bg-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-start gap-3">
            <span className="text-blue-400 text-lg mt-1">💬</span>
            <div>
              <span className="text-xs text-gray-500 uppercase">
                {currentQ.category}
              </span>
              <p className="text-white text-lg font-medium mt-1">
                {currentQ.text}
              </p>
            </div>
          </div>

          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Ta réponse..."
            rows={4}
            className="w-full bg-gray-900 text-white rounded-lg p-4 border border-gray-700 focus:border-blue-500 outline-none resize-none"
          />

          <button
            onClick={handleAnswer}
            disabled={!answer.trim()}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-lg font-semibold transition"
          >
            Envoyer la réponse
          </button>
        </div>
      )}

      {qaLog.length > 0 && (
        <details className="bg-gray-800/50 rounded-xl p-4">
          <summary className="text-sm text-gray-500 cursor-pointer">
            Historique ({qaLog.length} réponses)
          </summary>
          <div className="mt-3 space-y-3 text-sm">
            {qaLog.map((qa, i) => (
              <div key={i} className="border-l-2 border-gray-700 pl-3">
                <p className="text-blue-400">{qa.question}</p>
                <p className="text-gray-400 mt-1">{qa.answer}</p>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

function SpecStep({ sessionId }: { sessionId: string }) {
  const [spec, setSpec] = useState<{ raw_markdown: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useState(() => {
    (async () => {
      try {
        const data = await getSpec(sessionId);
        setSpec(data);
      } catch {
        /* retry once */
        try {
          const data = await getSpec(sessionId);
          setSpec(data);
        } catch {
          setSpec({ raw_markdown: "Erreur lors de la génération." });
        }
      }
      setLoading(false);
    })();
  });

  const copyToClipboard = () => {
    if (spec) {
      navigator.clipboard.writeText(spec.raw_markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="text-center text-gray-400 py-20">
        Génération du spec... (cela peut prendre ~30s)
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">
          📋 Spécification Technique
        </h2>
        <button
          onClick={copyToClipboard}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm transition"
        >
          {copied ? "✅ Copié !" : "📋 Copier le markdown"}
        </button>
      </div>

      <div className="bg-gray-800 rounded-xl p-6">
        <pre className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
          {spec?.raw_markdown || "Aucun contenu"}
        </pre>
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-green-700 hover:bg-green-600 text-white rounded-lg font-semibold transition"
        >
          🆕 Nouveau projet
        </button>
      </div>
    </div>
  );
}

// ---- App ----
export default function App() {
  const [step, setStep] = useState<Step>("record");
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      {/* Steps indicator */}
      <div className="max-w-xl mx-auto mb-8">
        <div className="flex justify-center gap-2 text-xs text-gray-600">
          {["record", "interview", "spec"].map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <span
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === s
                    ? "bg-blue-600 text-white"
                    : ["record", "interview", "spec"].indexOf(step) > i
                    ? "bg-green-700 text-white"
                    : "bg-gray-800 text-gray-500"
                }`}
              >
                {["record", "interview", "spec"].indexOf(step) > i
                  ? "✓"
                  : i + 1}
              </span>
              <span className="hidden sm:inline">
                {s === "record"
                  ? "Enregistrer"
                  : s === "interview"
                  ? "Interview"
                  : "Spec"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {step === "record" && (
        <RecordStep
          onDone={(sid) => {
            setSessionId(sid);
            setStep("interview");
          }}
        />
      )}
      {step === "interview" && sessionId && (
        <InterviewStep
          sessionId={sessionId}
          onDone={() => setStep("spec")}
        />
      )}
      {step === "spec" && sessionId && <SpecStep sessionId={sessionId} />}
    </div>
  );
}
