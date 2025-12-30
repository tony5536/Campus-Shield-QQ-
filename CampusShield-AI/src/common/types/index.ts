export type Incident = {
    id: string;
    title: string;
    description: string;
    location: string;
    timestamp: Date;
    status: 'reported' | 'in-progress' | 'resolved';
};

export type EmergencyAlert = {
    id: string;
    type: string;
    message: string;
    timestamp: Date;
    severity: 'low' | 'medium' | 'high';
};

export interface User {
    id: string;
    name: string;
    email: string;
    role: 'student' | 'staff' | 'admin';
}

export interface Location {
    latitude: number;
    longitude: number;
    description: string;
}