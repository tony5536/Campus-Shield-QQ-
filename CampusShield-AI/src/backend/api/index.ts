import { Router } from 'express';
import incidentRoutes from '../controllers/incidentController';

const apiRouter = Router();

apiRouter.use('/incidents', incidentRoutes);

export default apiRouter;