import { Body, Controller, Get, Param, Patch, Query } from '@nestjs/common';
import { IsDateString, IsOptional, IsUUID } from 'class-validator';
import { ProfilesService } from './profiles.service';

class UpdateDobDto {
  @IsDateString()
  dateOfBirth!: string;
}

@Controller('profiles')
export class ProfilesController {
  constructor(private readonly profiles: ProfilesService) {}

  @Get()
  findAll(@Query('userIds') userIds?: string) {
    if (userIds) {
      return this.profiles.findByUserIds(userIds.split(',').filter(Boolean));
    }
    return this.profiles.findAll();
  }

  @Get(':userId')
  findOne(@Param('userId') userId: string) {
    return this.profiles.findOne(userId);
  }

  @Patch(':userId')
  updateDob(@Param('userId') userId: string, @Body() dto: UpdateDobDto) {
    return this.profiles.updateDob(userId, dto.dateOfBirth);
  }
}
