import React, { Component } from "react";
import {Link, Navigate} from "react-router-dom";

type Props = {
    is_superuser: boolean,
}

type State = {
}

export default class Dashboard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        fetch("/api/playing_lemmas")
    }


    render() {
        return (
            <>
                {this.props.is_superuser && (
                    <div className="col-3 offset-3">
                        <Link to="/add_document">
                            <div className="big button">
                                Add document
                            </div>
                        </Link>
                    </div>
                )}
                <div className="col-3">
                    <Link to="/documents">
                        <div className="big button">
                            See documents
                        </div>
                    </Link>
                </div>
            </>
        );
    }
}
