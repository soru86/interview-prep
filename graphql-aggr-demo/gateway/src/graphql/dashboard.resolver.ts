import { Query, Resolver } from '@nestjs/graphql';
import { UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { DashboardService } from '../dashboard/dashboard.service';
import { Dashboard } from './models/dashboard.model';

@Resolver(() => Dashboard)
export class DashboardResolver {
  constructor(private readonly dashboardService: DashboardService) {}

  @Query(() => Dashboard, { name: 'dashboard' })
  @UseGuards(JwtAuthGuard)
  async dashboard(): Promise<Dashboard> {
    return this.dashboardService.getDashboard() as Promise<Dashboard>;
  }
}
