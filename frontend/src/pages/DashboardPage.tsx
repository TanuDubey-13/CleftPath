import React from 'react';
import {
  Compass,
  Calendar,
  Sparkles,
  HeartPulse,
  Mic,
  FileText,
  MessageSquare,
  ArrowRight,
  CheckCircle2,
  Clock,
  Send,
  Plus,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { useHealth } from '../hooks/useHealth';

export const DashboardPage: React.FC = () => {
  const { data: health } = useHealth();

  return (
    <div className="space-y-6 sm:space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-teal-900 to-teal-800 text-white rounded-3xl p-6 sm:p-8 shadow-warm-md">
        <div className="space-y-1.5 max-w-xl">
          <Badge variant="coral" size="sm" className="mb-1 text-white bg-coral-500 border-none">
            Active Milestone
          </Badge>
          <h1 className="font-heading font-bold text-2xl sm:text-3xl tracking-tight">
            Welcome back, Sarah
          </h1>
          <p className="text-teal-100/90 text-sm sm:text-base leading-relaxed">
            Baby Leo is in <strong className="text-white">Stage 2: Primary Lip Repair (3–6 Months)</strong>. Surgery is approximately 4 weeks away.
          </p>
        </div>
        <div className="flex sm:flex-col items-start sm:items-end justify-between gap-2">
          <Button
            variant="coral"
            size="md"
            rightIcon={<ArrowRight className="w-4 h-4" />}
            onClick={() => window.location.assign('/journey')}
          >
            View My Journey
          </Button>
          <span className="text-[11px] text-teal-200/80 font-mono">
            {health?.database.pgvector_available ? 'AI & RAG Engine Ready' : 'System Online'}
          </span>
        </div>
      </div>

      {/* 12-Column Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6">
        
        {/* CARD 1: MY JOURNEY PROGRESS (8-Col) */}
        <Card className="lg:col-span-8 flex flex-col justify-between" variant="interactive" onClick={() => window.location.assign('/journey')}>
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-stone-100">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
                  <Compass className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h3 className="font-heading font-bold text-base text-charcoal-900">Longitudinal Journey</h3>
                  <p className="text-xs text-charcoal-600">Stage 2 of 8 Developmental Phases</p>
                </div>
              </div>
              <Badge variant="sage" size="sm">65% Stage Complete</Badge>
            </div>

            {/* Visual Timeline Path Mini-Widget */}
            <div className="py-6 space-y-4">
              <div className="flex items-center justify-between text-xs font-semibold text-charcoal-600 px-2">
                <span className="flex items-center gap-1.5 text-sage-600">
                  <CheckCircle2 className="w-4 h-4" /> Stage 1: Feeding Prep
                </span>
                <span className="flex items-center gap-1.5 text-coral-600 font-bold">
                  <Clock className="w-4 h-4 animate-spin" /> Stage 2: Lip Repair
                </span>
                <span className="text-charcoal-400">Stage 3: Palate (9-18m)</span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-stone-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-sage-500 to-coral-500 h-full w-[65%] rounded-full transition-all duration-500"></div>
              </div>
            </div>

            {/* Next Milestone Action Item */}
            <div className="p-3.5 rounded-xl bg-ivory-50 border border-stone-200/80 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <span className="text-[11px] font-bold text-coral-600 uppercase tracking-wider">Next Milestone</span>
                <p className="text-xs sm:text-sm font-semibold text-charcoal-900 truncate">
                  Pre-Operative Bloodwork & Anesthesia Screening
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); window.location.assign('/journey'); }}>
                Checklist
              </Button>
            </div>
          </div>
        </Card>

        {/* CARD 2: UPCOMING APPOINTMENT (4-Col) */}
        <Card className="lg:col-span-4 flex flex-col justify-between" variant="interactive" onClick={() => window.location.assign('/appointments')}>
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-stone-100">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-teal-900" />
                <h3 className="font-heading font-bold text-sm text-charcoal-900">Upcoming Visit</h3>
              </div>
              <Badge variant="coral" size="sm">In 6 Days</Badge>
            </div>

            <div className="py-4 space-y-2">
              <p className="text-base font-bold text-teal-900">Dr. Robert Sterling, MD</p>
              <p className="text-xs text-charcoal-600 font-medium">Pediatric Plastic & Cleft Surgeon</p>
              <p className="text-xs text-charcoal-800 bg-stone-100/80 px-2.5 py-1.5 rounded-lg inline-block font-mono">
                Monday, Oct 14 • 10:00 AM
              </p>
            </div>
          </div>

          <Button
            variant="secondary"
            size="sm"
            className="w-full justify-center mt-2"
            rightIcon={<Sparkles className="w-3.5 h-3.5 text-teal-900" />}
            onClick={(e) => { e.stopPropagation(); window.location.assign('/appointments'); }}
          >
            Generate Question Prep-Sheet
          </Button>
        </Card>

        {/* CARD 3: PATHGUIDE SMART PROMPTS (12-Col) */}
        <Card className="lg:col-span-12 bg-gradient-to-br from-teal-50/70 via-white to-ivory-50 border-teal-200/80">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-coral-500" />
                <h3 className="font-heading font-bold text-base text-teal-900">PathGuide AI Assistant</h3>
                <Badge variant="teal" size="sm">Evidence Grounded</Badge>
              </div>
              <p className="text-xs sm:text-sm text-charcoal-600">
                Ask anything about feeding bottles, surgery prep checklists, or recovery timelines.
              </p>
            </div>

            {/* Quick Prompt Chips */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => window.location.assign('/pathguide?q=What+to+pack+for+lip+repair+surgery%3F')}
                className="text-xs px-3 py-1.5 rounded-xl bg-white border border-stone-200 hover:border-teal-700 hover:text-teal-900 text-charcoal-800 font-medium transition shadow-sm"
              >
                🎒 What to pack for lip surgery?
              </button>
              <button
                onClick={() => window.location.assign('/pathguide?q=How+to+clean+NAM+appliance+taping%3F')}
                className="text-xs px-3 py-1.5 rounded-xl bg-white border border-stone-200 hover:border-teal-700 hover:text-teal-900 text-charcoal-800 font-medium transition shadow-sm"
              >
                🧴 NAM appliance skin care tips
              </button>
            </div>
          </div>

          {/* Inline Chat Launcher */}
          <div className="mt-4 pt-3 border-t border-teal-100/80 flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask PathGuide a question about Baby Leo's care..."
              className="flex-1 bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  window.location.assign(`/pathguide?q=${encodeURIComponent((e.target as HTMLInputElement).value)}`);
                }
              }}
            />
            <Button
              variant="primary"
              size="md"
              rightIcon={<Send className="w-3.5 h-3.5" />}
              onClick={() => window.location.assign('/pathguide')}
            >
              Ask
            </Button>
          </div>
        </Card>

        {/* CARD 4: BABY & PARENT CARE (4-Col) */}
        <Card className="lg:col-span-4" variant="interactive" onClick={() => window.location.assign('/care')}>
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <HeartPulse className="w-4 h-4 text-sage-600" />
              <h3 className="font-heading font-bold text-sm text-charcoal-900">Baby Care & Feeding</h3>
            </div>
            <Badge variant="sage" size="sm">Today</Badge>
          </div>
          <div className="py-3 space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-charcoal-600">Total Intake:</span>
              <span className="font-mono font-bold text-base text-charcoal-900">680 ml</span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-charcoal-600">Bottle Method:</span>
              <span className="text-xs font-semibold text-teal-900">Dr. Brown's Specialty</span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-charcoal-600">Current Weight:</span>
              <span className="font-mono font-bold text-xs text-sage-700">6.2 kg (50th %ile)</span>
            </div>
          </div>
          <Button variant="outline" size="sm" className="w-full justify-center" leftIcon={<Plus className="w-3 h-3" />}>
            Log Feeding Session
          </Button>
        </Card>

        {/* CARD 5: VOICE JOURNEY (4-Col) */}
        <Card className="lg:col-span-4" variant="interactive" onClick={() => window.location.assign('/voice')}>
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <Mic className="w-4 h-4 text-coral-500" />
              <h3 className="font-heading font-bold text-sm text-charcoal-900">Voice Journey</h3>
            </div>
            <Badge variant="stone" size="sm">Pre-Speech</Badge>
          </div>
          <div className="py-3 space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-charcoal-600">Target Sounds:</span>
              <span className="font-mono font-bold text-xs text-teal-900">/p/ & /b/ Babbling</span>
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-xs text-charcoal-600">Weekly Goal:</span>
              <span className="text-xs font-semibold text-sage-600">3 of 5 Days Completed</span>
            </div>
            <p className="text-[11px] text-charcoal-500 italic">
              Encourage early bilabial consonant games before lip repair.
            </p>
          </div>
          <Button variant="outline" size="sm" className="w-full justify-center">
            Record Audio Practice
          </Button>
        </Card>

        {/* CARD 6: DOCUMENT VAULT (4-Col) */}
        <Card className="lg:col-span-4" variant="interactive" onClick={() => window.location.assign('/journey')}>
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-teal-900" />
              <h3 className="font-heading font-bold text-sm text-charcoal-900">Recent Medical Record</h3>
            </div>
            <Badge variant="sage" size="sm">Verified</Badge>
          </div>
          <div className="py-3 space-y-1.5">
            <p className="text-xs font-bold text-charcoal-900 truncate">Audiology Hearing Screen.pdf</p>
            <p className="text-[11px] text-charcoal-600">Children's Craniofacial Center</p>
            <p className="text-[11px] text-sage-700 bg-sage-50 px-2 py-1 rounded-md font-medium">
              ✓ Bilateral normal hearing confirmed
            </p>
          </div>
          <Button variant="outline" size="sm" className="w-full justify-center">
            Upload Document (OCR)
          </Button>
        </Card>

        {/* CARD 7 & 8: THE VILLAGE & CLINICAL NOTICE (12-Col) */}
        <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card variant="interactive" onClick={() => window.location.assign('/village')}>
            <div className="flex items-center justify-between pb-3 border-b border-stone-100">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-teal-900" />
                <h3 className="font-heading font-bold text-sm text-charcoal-900">The Village Community</h3>
              </div>
              <Badge variant="teal" size="sm">#Stage2Club</Badge>
            </div>
            <div className="py-3 space-y-1.5">
              <p className="text-xs font-bold text-charcoal-900">
                "Tips for post-op arm restraints (No-Nos) during tummy time?"
              </p>
              <p className="text-xs text-charcoal-600">
                14 parents shared comforting advice and soft fabric alternatives.
              </p>
            </div>
          </Card>

          <Alert
            variant="info"
            title="Non-Diagnostic Health Platform"
          >
            CleftPath is an educational and organizational tool. Always consult your accredited cleft team for medical evaluations.
          </Alert>
        </div>

      </div>
    </div>
  );
};
