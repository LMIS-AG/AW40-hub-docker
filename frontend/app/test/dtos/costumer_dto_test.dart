import "package:aw40_hub_frontend/dtos/costumer_dto.dart";
import "package:aw40_hub_frontend/models/costumer_model.dart";
import "package:aw40_hub_frontend/utils/enums.dart";
import "package:flutter_test/flutter_test.dart";

void main() {
  group("CostumerDto primary constructor", () {
    const id = AnonymousCustomerId.anonymous;
    final CostumerDto costumerDto = CostumerDto(
      id,
    );
    test("correctly assigns id", () {
      expect(costumerDto.id, id);
    });
  });
  group("costumerDto fromJson constructor", () {
    const id = AnonymousCustomerId.anonymous;
    final Map<String, dynamic> json = <String, dynamic>{
      "_id": id.name,
    };
    final CostumerDto costumerDto = CostumerDto.fromJson(json);
    test("correctly assigns id", () {
      expect(costumerDto.id, id);
    });
  });
  group("VehicleDto toJson method", () {
    const id = AnonymousCustomerId.anonymous;
    final CostumerDto costumerDto = CostumerDto(
      id,
    );
    final Map<String, dynamic> json = costumerDto.toJson();
    test("correctly assigns id", () {
      expect(json["_id"], id.name);
    });
  });

  group("CostumerDto toModel method", () {
    const id = AnonymousCustomerId.anonymous;
    final CostumerDto costumerDto = CostumerDto(
      id,
    );
    final CostumerModel costumerModel = costumerDto.toModel();
    test("correctly assigns id", () {
      expect(costumerModel.id, id);
    });
  });
}
