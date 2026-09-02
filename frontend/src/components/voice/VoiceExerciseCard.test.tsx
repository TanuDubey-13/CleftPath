import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { VoiceExerciseCard } from './VoiceExerciseCard';
import { VoiceExercise } from '../../types';

const mockExercise: VoiceExercise = {
  id: 'ex-123',
  title: 'Infant Bilabial Sound Exploration',
  target_phonemes: ['p', 'b', 'm'],
  stage_id: 2,
  prompt_text: 'Gentle repetitive /pa-pa-pa/ babbling games.',
  instructions: 'Maintain direct eye contact and smile when imitating lip closure.',
  difficulty_level: 'beginner',
  created_at: '2026-09-02T10:00:00Z',
};

describe('VoiceExerciseCard Component', () => {
  it('renders exercise title, target phonemes, and prompt', () => {
    render(
      <VoiceExerciseCard
        exercise={mockExercise}
        onSelectPractice={vi.fn()}
        onViewDetails={vi.fn()}
      />
    );

    expect(screen.getByText('Infant Bilabial Sound Exploration')).toBeInTheDocument();
    expect(screen.getByText('/p/')).toBeInTheDocument();
    expect(screen.getByText('/b/')).toBeInTheDocument();
    expect(screen.getByText('/m/')).toBeInTheDocument();
    expect(screen.getByText('"Gentle repetitive /pa-pa-pa/ babbling games."')).toBeInTheDocument();
  });

  it('triggers onSelectPractice when Start Practice is clicked', () => {
    const handleSelect = vi.fn();
    render(
      <VoiceExerciseCard
        exercise={mockExercise}
        onSelectPractice={handleSelect}
        onViewDetails={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /start practice/i }));
    expect(handleSelect).toHaveBeenCalledWith(mockExercise);
  });

  it('triggers onViewDetails when Details button is clicked', () => {
    const handleDetails = vi.fn();
    render(
      <VoiceExerciseCard
        exercise={mockExercise}
        onSelectPractice={vi.fn()}
        onViewDetails={handleDetails}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /details/i }));
    expect(handleDetails).toHaveBeenCalledWith(mockExercise);
  });
});
