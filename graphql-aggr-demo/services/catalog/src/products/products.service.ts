import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { In, Repository } from 'typeorm';
import { ProductEntity } from '../entities/product.entity';

@Injectable()
export class ProductsService {
  constructor(
    @InjectRepository(ProductEntity)
    private readonly products: Repository<ProductEntity>,
  ) {}

  findAll() {
    return this.products.find();
  }

  async upsert(sku: string, name: string, inventoryCount: number) {
    const existing = await this.products.findOne({ where: { sku } });
    if (existing) {
      existing.name = name;
      existing.inventoryCount = inventoryCount;
      return this.products.save(existing);
    }
    return this.products.save(this.products.create({ sku, name, inventoryCount }));
  }

  findBySkus(skus: string[]) {
    if (!skus.length) return [];
    return this.products.find({ where: { sku: In(skus) } });
  }

  async decrementInventory(sku: string, quantity: number) {
    const product = await this.products.findOne({ where: { sku } });
    if (!product) return null;
    product.inventoryCount = Math.max(0, product.inventoryCount - quantity);
    return this.products.save(product);
  }
}
