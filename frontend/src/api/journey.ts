import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  JourneyMilestone,
  JourneyOverview,
  JourneyStage,
  MilestoneNote,
  MilestoneNoteCreateRequest,
  MilestoneUpdateRequest,
} from '../types';

export const fetchJourneyOverview = async (
  patientId?: string
): Promise<JourneyOverview> => {
  const url = patientId ? `/journey?patient_id=${patientId}` : '/journey';
  const response = await apiClient.get<ApiResponse<JourneyOverview>>(url);
  return response.data.data;
};

export const fetchJourneyStages = async (): Promise<JourneyStage[]> => {
  const response = await apiClient.get<ApiResponse<JourneyStage[]>>('/journey/stages');
  return response.data.data;
};

export const fetchMilestoneDetail = async (
  milestoneId: string
): Promise<JourneyMilestone> => {
  const response = await apiClient.get<ApiResponse<JourneyMilestone>>(
    `/journey/milestones/${milestoneId}`
  );
  return response.data.data;
};

export const updateMilestoneProgress = async (
  milestoneId: string,
  payload: MilestoneUpdateRequest
): Promise<JourneyMilestone> => {
  const response = await apiClient.patch<ApiResponse<JourneyMilestone>>(
    `/journey/milestones/${milestoneId}`,
    payload
  );
  return response.data.data;
};

export const fetchMilestoneNotes = async (
  milestoneId: string
): Promise<MilestoneNote[]> => {
  const response = await apiClient.get<ApiResponse<MilestoneNote[]>>(
    `/journey/milestones/${milestoneId}/notes`
  );
  return response.data.data;
};

export const addMilestoneNote = async (
  milestoneId: string,
  payload: MilestoneNoteCreateRequest
): Promise<MilestoneNote> => {
  const response = await apiClient.post<ApiResponse<MilestoneNote>>(
    `/journey/milestones/${milestoneId}/notes`,
    payload
  );
  return response.data.data;
};
