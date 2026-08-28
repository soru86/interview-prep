import { Body, Controller, Get, Post } from '@nestjs/common';
import { IsInt, IsString, IsUUID, Min } from 'class-validator';
import { OrdersService } from './orders.service';

class CreateOrderDto {
  @IsUUID()
  userId!: string;

  @IsString()
  productSku!: string;

  @IsInt()
  @Min(1)
  quantity!: number;
}

@Controller('orders')
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Get()
  findAll() {
    return this.orders.findAll();
  }

  @Post()
  create(@Body() dto: CreateOrderDto) {
    return this.orders.create(dto.userId, dto.productSku, dto.quantity);
  }
}
