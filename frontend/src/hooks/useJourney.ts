import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  addMilestoneNote,
  fetchJourneyOverview,
  updateMilestoneProgress,
} from '../api/journey';
import { MilestoneNoteCreateRequest, MilestoneUpdateRequest } from '../types';

export const useJourney = (patientId?: string) => {
  return useQuery({
    queryKey: ['journey', patientId || 'primary'],
    queryFn: () => fetchJourneyOverview(patientId),
    staleTime: 2 * 60 * 1000,
  });
};

export const useUpdateMilestone = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      milestoneId,
      payload,
    }: {
      milestoneId: string;
      payload: MilestoneUpdateRequest;
    }) => updateMilestoneProgress(milestoneId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journey'] });
    },
  });
};

export const useAddMilestoneNote = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      milestoneId,
      payload,
    }: {
      milestoneId: string;
      payload: MilestoneNoteCreateRequest;
    }) => addMilestoneNote(milestoneId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journey'] });
    },
  });
};
