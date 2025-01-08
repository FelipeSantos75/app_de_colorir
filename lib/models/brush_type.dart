enum BrushType {
  basic,
  pencil,
  chalk;

  String get name {
    switch (this) {
      case BrushType.basic:
        return 'Pincel Básico';
      case BrushType.pencil:
        return 'Lápis';
      case BrushType.chalk:
        return 'Giz';
    }
  }

  String get icon {
    switch (this) {
      case BrushType.basic:
        return 'assets/icons/brush.png';
      case BrushType.pencil:
        return 'assets/icons/pencil.png';
      case BrushType.chalk:
        return 'assets/icons/chalk.png';
    }
  }
  
  String get description {
    switch (this) {
      case BrushType.basic:
        return 'Preenchimento sólido uniforme';
      case BrushType.pencil:
        return 'Textura de lápis de cor';
      case BrushType.chalk:
        return 'Textura granulada de giz';
    }
  }

  bool get isPremium {
    switch (this) {
      case BrushType.basic:
        return false;
      case BrushType.pencil:
      case BrushType.chalk:
        return true;
    }
  }
}