class ActionModel {
  ActionModel(
    this.id,
    this.instruction,
    this.actionType,
    this.dataType,
    this.component,
  );

  String id;
  String instruction;
  dynamic actionType;
  dynamic dataType;
  dynamic component;
}
