import "package:flutter/material.dart";

class DesktopAppBar extends StatelessWidget {
  const DesktopAppBar({
    required this.title,
    required this.actions,
    super.key,
  });
  final String title;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 90,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Row(
          children: <Widget>[
            Text(title, style: Theme.of(context).textTheme.displayMedium),
            const Spacer(),
            if (actions != null) Row(children: actions!)
          ],
        ),
      ),
    );
  }
}
