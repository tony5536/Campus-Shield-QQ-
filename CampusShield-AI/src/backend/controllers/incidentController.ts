export class IncidentController {
    constructor(private emergencyService: EmergencyService) {}

    async createIncident(req, res) {
        try {
            const incidentData = req.body;
            const newIncident = await this.emergencyService.createIncident(incidentData);
            res.status(201).json(newIncident);
        } catch (error) {
            res.status(500).json({ message: 'Error creating incident', error });
        }
    }

    async getIncident(req, res) {
        try {
            const { id } = req.params;
            const incident = await this.emergencyService.getIncidentById(id);
            if (!incident) {
                return res.status(404).json({ message: 'Incident not found' });
            }
            res.status(200).json(incident);
        } catch (error) {
            res.status(500).json({ message: 'Error retrieving incident', error });
        }
    }

    async updateIncident(req, res) {
        try {
            const { id } = req.params;
            const incidentData = req.body;
            const updatedIncident = await this.emergencyService.updateIncident(id, incidentData);
            if (!updatedIncident) {
                return res.status(404).json({ message: 'Incident not found' });
            }
            res.status(200).json(updatedIncident);
        } catch (error) {
            res.status(500).json({ message: 'Error updating incident', error });
        }
    }
}