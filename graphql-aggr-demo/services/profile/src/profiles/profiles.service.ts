import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { In, Repository } from 'typeorm';
import { ProfileEntity } from '../entities/profile.entity';

@Injectable()
export class ProfilesService {
  constructor(
    @InjectRepository(ProfileEntity)
    private readonly profiles: Repository<ProfileEntity>,
  ) {}

  createFromRegistration(userId: string, email: string) {
    return this.profiles.save(this.profiles.create({ userId, email, dateOfBirth: null }));
  }

  findAll() {
    return this.profiles.find();
  }

  findByUserIds(userIds: string[]) {
    if (!userIds.length) return [];
    return this.profiles.find({ where: { userId: In(userIds) } });
  }

  async findOne(userId: string) {
    const profile = await this.profiles.findOne({ where: { userId } });
    if (!profile) throw new NotFoundException('Profile not found');
    return profile;
  }

  async updateDob(userId: string, dateOfBirth: string) {
    const profile = await this.findOne(userId);
    profile.dateOfBirth = dateOfBirth;
    return this.profiles.save(profile);
  }
}
