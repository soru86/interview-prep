import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { HttpModule } from '@nestjs/axios';
import { join } from 'path';
import { ConsulRegistry } from '@graphql-aggr/service-mesh';
import { DashboardResolver } from './dashboard.resolver';
import { DashboardService } from '../dashboard/dashboard.service';
import { BackendClientService } from '../clients/backend-client.service';

@Module({
  imports: [
    HttpModule,
    GraphQLModule.forRoot<ApolloDriverConfig>({
      driver: ApolloDriver,
      autoSchemaFile: join(process.cwd(), 'src/schema.gql'),
      sortSchema: true,
      playground: true,
    }),
  ],
  providers: [DashboardResolver, DashboardService, BackendClientService, ConsulRegistry],
})
export class GraphqlModule {}
