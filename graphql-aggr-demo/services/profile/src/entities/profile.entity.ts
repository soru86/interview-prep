import { Column, Entity, PrimaryColumn, UpdateDateColumn } from 'typeorm';

@Entity('profiles')
export class ProfileEntity {
  @PrimaryColumn({ name: 'user_id' })
  userId!: string;

  @Column()
  email!: string;

  @Column({ name: 'date_of_birth', type: 'date', nullable: true })
  dateOfBirth!: string | null;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt!: Date;
}
