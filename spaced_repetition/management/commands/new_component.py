from django.core.management.base import BaseCommand

CONTENTS = """import React, { Component } from "react";

type Props = {
}

type State = {
}

export default class %s extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
    };
  }


  render() {
    return (
      <>
      </>
    );
  }
}
"""


class Command(BaseCommand):
    help = 'Transpiles Django models into a Typescript type definition file'

    def add_arguments(self, parser):
        parser.add_argument('component_names', nargs='+', type=str)

    def handle(self, *args, component_names, **options):
        for name in component_names:
            with open(f"src/{name}.tsx", "w") as fh:
                fh.write(CONTENTS % name)


