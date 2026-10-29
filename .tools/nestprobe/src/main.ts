import 'reflect-metadata';
import { Controller, Get, Injectable, Module } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';

@Injectable()
class HealthService {
  status(): string {
    return 'ok';
  }
}

@Controller('health')
class HealthController {
  constructor(private readonly svc: HealthService) {}

  @Get()
  check(): { status: string } {
    return { status: this.svc.status() };
  }
}

@Module({ controllers: [HealthController], providers: [HealthService] })
class AppModule {}

async function main(): Promise<void> {
  const app = await NestFactory.create(AppModule, { logger: false });
  await app.listen(3111);

  const res = await fetch('http://127.0.0.1:3111/health');
  console.log('INYECCION+HTTP:', res.status, await res.text());

  await app.close();
  console.log('NESTJS VERIFICADO');
}

main().catch((err: unknown) => {
  console.error('FALLO:', err);
  process.exit(1);
});
