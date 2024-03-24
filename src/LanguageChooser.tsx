import React, { Component } from "react";
import { Navigate } from "react-router-dom";
import { Language } from "./models";
import {LoggedInUserState} from "./types";
import {safePost} from "./ajax_utils";

type Props = {
    user_state: LoggedInUserState,
    reloadUserState: () => void,
}

type State = {
    choices?: Language[],
}

export default class LanguageChooser extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        fetch("/api/languages")
            .then(res => res.json())
            .then(data => this.setState({
                choices: data,
            }))
    }

    chooseLanguage(language: Language) {
        safePost(
            "/api/choose_language",
            {language: language.id},
        ).then(() => this.props.reloadUserState())
    }

    render() {
        if (this.props.user_state.current_language !== null) {
            return <Navigate to="/"/>;
        }

        if (this.state.choices === undefined) {
            return null;
        }

        return <>
            <h2 style={{textAlign: "center"}}>
                What language would you like to learn?
            </h2>

            <div className="col-12 col-md-8 col-lg-6 offset-md-2 offset-lg-3">
                {this.state.choices.map((l: Language) => (
                    <div className="button" onClick={() => this.chooseLanguage(l)} key={l.name}>
                        {l.name}
                    </div>
                ))}
            </div>
        </>;
    }
}
