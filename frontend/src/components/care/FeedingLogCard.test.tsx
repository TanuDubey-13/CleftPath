import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { FeedingLogCard } from './FeedingLogCard';
import { FeedingLog } from '../../types';

const mockFeedingLog: FeedingLog = {
  id: 'feed_123',
  patient_id: 'pt_456',
  logged_at: '2026-09-02T08:30:00Z',
  bottle_type: 'dr_browns_specialty',
  volume_ml: 110,
  duration_minutes: 25,
  burping_breaks: 3,
  reflux_severity: 'mild',
  notes: 'Fed upright with blue valve',
  created_at: '2026-09-02T08:30:00Z',
};

describe('FeedingLogCard Component', () => {
  it('renders volume, bottle type, duration, and reflux severity', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();

    render(<FeedingLogCard log={mockFeedingLog} onEdit={onEdit} onDelete={onDelete} />);

    expect(screen.getByText('110')).toBeInTheDocument();
    expect(screen.getByText(/Dr. Brown's Specialty Feeder/i)).toBeInTheDocument();
    expect(screen.getByText(/25 min • 3 burps/i)).toBeInTheDocument();
    expect(screen.getByText(/Reflux: MILD/i)).toBeInTheDocument();
    expect(screen.getByText('Fed upright with blue valve')).toBeInTheDocument();
  });

  it('triggers edit and delete handlers', async () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();

    render(<FeedingLogCard log={mockFeedingLog} onEdit={onEdit} onDelete={onDelete} />);

    const editBtn = screen.getByLabelText(/edit feeding session/i);
    await userEvent.click(editBtn);
    expect(onEdit).toHaveBeenCalledWith(mockFeedingLog);

    const deleteBtn = screen.getByLabelText(/delete feeding session/i);
    await userEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledWith('feed_123');
  });
});
