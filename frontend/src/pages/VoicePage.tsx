import React from 'react';
import { Mic, Play } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';

export const VoicePage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">Voice Journey</h1>
          <p className="text-sm text-charcoal-600">
            Supportive home practice companion for pre-speech exploration and articulation awareness.
          </p>
        </div>
      </div>

      <Alert variant="info" title="Speech Therapy Practice Notice">
        Voice Journey is a home exercise log and acoustic awareness tool. It does NOT diagnose speech disorders, hypernasality, or velopharyngeal insufficiency (VPI). Always consult your licensed Speech-Language Pathologist (SLP).
      </Alert>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-heading font-bold text-base text-charcoal-900">Infant Babbling Exercise</h3>
            <Badge variant="coral" size="sm">Stage 2 Pre-Speech</Badge>
          </div>
          <p className="text-xs text-charcoal-600 leading-relaxed">
            Target bilabial consonants: Practice gentle repetitive "/pa-pa-pa/" and "/ba-ba-ba/" games while making direct eye contact.
          </p>
          <div className="p-4 bg-teal-50 rounded-2xl flex flex-col items-center justify-center gap-3">
            <div className="w-16 h-16 rounded-full bg-teal-900 text-white flex items-center justify-center shadow-warm-md hover:scale-105 transition cursor-pointer">
              <Mic className="w-7 h-7 text-coral-400" />
            </div>
            <span className="text-xs font-bold text-teal-900">Tap to Start 60-Second Audio Recording</span>
          </div>
        </Card>

        <Card className="space-y-4">
          <h3 className="font-heading font-bold text-base text-charcoal-900">Audio Diary & SLP Export</h3>
          <p className="text-xs text-charcoal-600 leading-relaxed">
            Saved audio clips can be exported as a timeline for your SLP to review articulation progress before and after palate repair.
          </p>
          <div className="space-y-2">
            <div className="p-3 bg-stone-50 rounded-xl flex items-center justify-between text-xs">
              <span className="font-semibold text-charcoal-800">Recording_Sep01_Bilabials.wav</span>
              <Button variant="ghost" size="sm" leftIcon={<Play className="w-3.5 h-3.5" />}>Play</Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
