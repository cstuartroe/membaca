import React, { Component } from "react";
import {Language} from "./models";
import {safePost} from "./ajax_utils";
import {Navigate} from "react-router-dom";

type Props = {
    reloadUserState: () => void,
}

type State = {
    choices?: Language[],
    selected: boolean,
}

export default class LanguageChooser extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            selected: false,
        };
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
            .then(() => this.setState({selected: true}));
    }

    nextDestination() {
        const params = new URLSearchParams(window.location.search);
        return params.get("next") || "/";
    }

    render() {
        if (this.state.choices === undefined) {
            return null;
        }

        if (this.state.selected) {
            return <Navigate to={this.nextDestination()}/>
        }

        return <>
            <div className="col-12 col-md-8 col-lg-6 offset-md-2 offset-lg-3">
                <h2>What language would you like to learn?</h2>

                {this.state.choices.map((l: Language) => (
                    <div className="big button" onClick={() => this.chooseLanguage(l)} key={l.name}>
                        {l.name}
                    </div>
                ))}
            </div>
        </>;
    }
}
