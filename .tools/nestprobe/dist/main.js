"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
require("reflect-metadata");
const common_1 = require("@nestjs/common");
const core_1 = require("@nestjs/core");
let HealthService = class HealthService {
    status() {
        return 'ok';
    }
};
HealthService = __decorate([
    (0, common_1.Injectable)()
], HealthService);
let HealthController = class HealthController {
    svc;
    constructor(svc) {
        this.svc = svc;
    }
    check() {
        return { status: this.svc.status() };
    }
};
__decorate([
    (0, common_1.Get)(),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Object)
], HealthController.prototype, "check", null);
HealthController = __decorate([
    (0, common_1.Controller)('health'),
    __metadata("design:paramtypes", [HealthService])
], HealthController);
let AppModule = class AppModule {
};
AppModule = __decorate([
    (0, common_1.Module)({ controllers: [HealthController], providers: [HealthService] })
], AppModule);
async function main() {
    const app = await core_1.NestFactory.create(AppModule, { logger: false });
    await app.listen(3111);
    const res = await fetch('http://127.0.0.1:3111/health');
    console.log('INYECCION+HTTP:', res.status, await res.text());
    await app.close();
    console.log('NESTJS VERIFICADO');
}
main().catch((err) => {
    console.error('FALLO:', err);
    process.exit(1);
});
