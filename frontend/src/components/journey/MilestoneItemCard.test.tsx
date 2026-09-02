import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MilestoneItemCard } from './MilestoneItemCard';
import { JourneyMilestone } from '../../types';

const mockMilestone: JourneyMilestone = {
  id: 'm_123',
  patient_id: 'p_456',
  stage_id: 1,
  title: 'Initial Cleft Team Consultation',
  description: 'Multidisciplinary team evaluation',
  target_age_months: 0,
  status: 'in_progress',
  is_custom: false,
  notes_count: 2,
  notes: [],
};

describe('MilestoneItemCard Component', () => {
  it('renders milestone title, description, and status pill', () => {
    const onSelect = vi.fn();
    const onToggle = vi.fn();

    render(
      <MilestoneItemCard
        milestone={mockMilestone}
        onSelect={onSelect}
        onToggleStatus={onToggle}
      />
    );

    expect(screen.getByText('Initial Cleft Team Consultation')).toBeInTheDocument();
    expect(screen.getByText('Multidisciplinary team evaluation')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('At Birth')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('calls onToggleStatus when status toggle button is clicked', async () => {
    const onSelect = vi.fn();
    const onToggle = vi.fn();

    render(
      <MilestoneItemCard
        milestone={mockMilestone}
        onSelect={onSelect}
        onToggleStatus={onToggle}
      />
    );

    const toggleBtn = screen.getByRole('button', { name: /mark completed/i });
    await userEvent.click(toggleBtn);

    expect(onToggle).toHaveBeenCalledWith('m_123', 'in_progress');
  });

  it('calls onSelect when the card container is clicked', async () => {
    const onSelect = vi.fn();
    const onToggle = vi.fn();

    render(
      <MilestoneItemCard
        milestone={mockMilestone}
        onSelect={onSelect}
        onToggleStatus={onToggle}
      />
    );

    const titleElement = screen.getByText('Initial Cleft Team Consultation');
    await userEvent.click(titleElement);

    expect(onSelect).toHaveBeenCalledWith(mockMilestone);
  });
});
