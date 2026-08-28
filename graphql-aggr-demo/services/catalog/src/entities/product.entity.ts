import { Column, Entity, PrimaryColumn } from 'typeorm';

@Entity('products')
export class ProductEntity {
  @PrimaryColumn()
  sku!: string;

  @Column()
  name!: string;

  @Column({ name: 'inventory_count', type: 'int' })
  inventoryCount!: number;
}
