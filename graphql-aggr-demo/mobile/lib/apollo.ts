import {
  ApolloClient,
  ApolloLink,
  HttpLink,
  InMemoryCache,
  gql,
  from,
} from '@apollo/client';
import { getAccessToken, refreshAccessToken } from './auth';

const httpLink = new HttpLink({
  uri: process.env.EXPO_PUBLIC_GATEWAY_URL ?? 'https://localhost:4000/graphql',
});

const authLink = new ApolloLink((operation, forward) => {
  return new Promise((resolve) => {
    getAccessToken().then((token) => {
      operation.setContext({
        headers: token ? { authorization: `Bearer ${token}` } : {},
      });
      resolve(forward(operation));
    });
  });
});

const errorLink = new ApolloLink((operation, forward) => {
  return forward(operation).map((response) => {
    const errors = response.errors;
    if (errors?.some((e) => e.extensions?.code === 'UNAUTHENTICATED' || e.message.includes('Unauthorized'))) {
      refreshAccessToken().then(() => {});
    }
    return response;
  });
});

export const apollo = new ApolloClient({
  link: from([authLink, errorLink, httpLink]),
  cache: new InMemoryCache(),
});

export const DASHBOARD_QUERY = gql`
  query Dashboard {
    dashboard {
      orderInsights {
        orderId
        productSku
        productName
        quantity
        notificationStatus
        notificationDetail
        inventoryRemaining
      }
      activeUsers {
        userId
        email
        loggedInAt
        dateOfBirth
      }
    }
  }
`;
