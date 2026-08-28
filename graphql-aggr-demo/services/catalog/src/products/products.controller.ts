import { Body, Controller, Get, Post, Query } from '@nestjs/common';
import { IsInt, IsString, Min } from 'class-validator';
import { ProductsService } from './products.service';

class SeedProductDto {
  @IsString()
  sku!: string;

  @IsString()
  name!: string;

  @IsInt()
  @Min(0)
  inventoryCount!: number;
}

@Controller('products')
export class ProductsController {
  constructor(private readonly products: ProductsService) {}

  @Post('seed')
  seed(@Body() dto: SeedProductDto) {
    return this.products.upsert(dto.sku, dto.name, dto.inventoryCount);
  }

  @Get()
  findAll() {
    return this.products.findAll();
  }

  @Get('by-skus')
  bySkus(@Query('skus') skus?: string) {
    return this.products.findBySkus(skus?.split(',').filter(Boolean) ?? []);
  }
}
