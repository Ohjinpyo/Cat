import React, { useState, useEffect } from 'react';
import Chart from "../../mainPage/Chart";
import styled from "styled-components";
import axios from "axios";
import {UserContext, useUser} from '../../../UserContext';

function AutoTradingPage() {
    const {username} = useUser();

    return (
        <div>
            <Chart />
        </div>

    );
}

export default AutoTradingPage;