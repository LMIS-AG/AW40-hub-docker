import "package:aw40_hub_frontend/models/action_model.dart";
import "package:json_annotation/json_annotation.dart";

part "action_dto.g.dart";

@JsonSerializable()
class ActionDto {
  ActionDto(
    this.id,
    this.instruction,
    this.actionType,
    this.dataType,
    this.component,
  );

  factory ActionDto.fromJson(Map<String, dynamic> json) {
    return _$ActionDtoFromJson(json);
  }

  ActionModel toModel() {
    return ActionModel(
      id,
      instruction,
      actionType,
      dataType,
      component,
    );
  }

  String id;
  String instruction;
  @JsonKey(name: "action_type")
  dynamic actionType;
  @JsonKey(name: "data_type")
  dynamic dataType;
  dynamic component;
}
