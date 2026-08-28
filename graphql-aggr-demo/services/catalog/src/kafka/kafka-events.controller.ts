import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { ProductsService } from '../products/products.service';

@Controller()
export class KafkaEventsController {
  constructor(private readonly products: ProductsService) {}

  @EventPattern('order.created')
  async onOrderCreated(
    @Payload() data: { productSku: string; quantity: number },
  ) {
    await this.products.decrementInventory(data.productSku, data.quantity);
  }
}
