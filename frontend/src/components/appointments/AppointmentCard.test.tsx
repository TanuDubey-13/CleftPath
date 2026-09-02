import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { AppointmentCard } from './AppointmentCard';
import { Appointment } from '../../types';

const mockAppointment: Appointment = {
  id: 'app_123',
  patient_id: 'pt_456',
  specialist_name: 'Dr. Robert Sterling',
  specialty: 'Plastic & Reconstructive Cleft Surgeon',
  clinic_location: "Children's Craniofacial Center, Suite 402",
  scheduled_at: '2026-10-14T10:00:00Z',
  duration_minutes: 45,
  prep_questions: ['What is the fasting window?', 'How to manage post-op tape?'],
  summary_notes: 'Reviewed incision lines.',
  status: 'scheduled',
  created_at: '2026-09-02T10:00:00Z',
  updated_at: '2026-09-02T10:00:00Z',
};

describe('AppointmentCard Component', () => {
  it('renders specialist name, specialty, location, and status', () => {
    const onSelect = vi.fn();
    render(<AppointmentCard appointment={mockAppointment} onSelect={onSelect} />);

    expect(screen.getByText('Dr. Robert Sterling')).toBeInTheDocument();
    expect(screen.getByText('Plastic & Reconstructive Cleft Surgeon')).toBeInTheDocument();
    expect(screen.getByText(/Children's Craniofacial Center/i)).toBeInTheDocument();
    expect(screen.getByText('SCHEDULED')).toBeInTheDocument();
    expect(screen.getByText('45 min visit')).toBeInTheDocument();
    expect(screen.getByText('2 questions')).toBeInTheDocument();
  });

  it('triggers onSelect when card is clicked', async () => {
    const onSelect = vi.fn();
    render(<AppointmentCard appointment={mockAppointment} onSelect={onSelect} />);

    const card = screen.getByText('Dr. Robert Sterling');
    await userEvent.click(card);

    expect(onSelect).toHaveBeenCalledWith(mockAppointment);
  });
});
