import React, { Component } from "react";
import {Language} from "./models";

type Props = {
    choices: Language[],
    choose: (l: Language) => void;
}

type State = {
}

export default class LanguageChooser extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {};
    }


    render() {
        return (
            <div className="col-12">
                <h2 style={{textAlign: "center"}}>
                    What language would you like to learn?
                </h2>

                <div className="col-12 col-md-8 col-lg-6 offset-md-2 offset-lg-3">
                    {this.props.choices.map((l: Language) => (
                        <div className="button" onClick={() => this.props.choose(l)}>
                            {l.name}
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}
