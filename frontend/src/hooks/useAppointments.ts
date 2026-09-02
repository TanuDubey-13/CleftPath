import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  cancelAppointment,
  createAppointment,
  fetchAppointmentDetail,
  fetchAppointments,
  fetchCareTeamMembers,
  updateAppointment,
} from '../api/appointments';
import {
  AppointmentCreateRequest,
  AppointmentQueryParams,
  AppointmentUpdateRequest,
} from '../types';

export const useAppointments = (params: AppointmentQueryParams = {}) => {
  return useQuery({
    queryKey: ['appointments', params],
    queryFn: () => fetchAppointments(params),
    staleTime: 2 * 60 * 1000,
  });
};

export const useAppointment = (appointmentId?: string) => {
  return useQuery({
    queryKey: ['appointment', appointmentId],
    queryFn: () => {
      if (!appointmentId) throw new Error('Appointment ID is required');
      return fetchAppointmentDetail(appointmentId);
    },
    enabled: !!appointmentId,
  });
};

export const useCreateAppointment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AppointmentCreateRequest) => createAppointment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    },
  });
};

export const useUpdateAppointment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      appointmentId,
      payload,
    }: {
      appointmentId: string;
      payload: AppointmentUpdateRequest;
    }) => updateAppointment(appointmentId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['appointment', variables.appointmentId] });
    },
  });
};

export const useCancelAppointment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (appointmentId: string) => cancelAppointment(appointmentId),
    onSuccess: (_, appointmentId) => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['appointment', appointmentId] });
    },
  });
};

export const useCareTeamMembers = (patientId?: string) => {
  return useQuery({
    queryKey: ['careTeamMembers', patientId || 'primary'],
    queryFn: () => fetchCareTeamMembers(patientId),
    staleTime: 5 * 60 * 1000,
  });
};
