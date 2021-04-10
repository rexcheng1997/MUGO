import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router } from 'react-router-dom';

import MUGO from 'components/MUGO';

ReactDOM.render(<Router><MUGO/></Router>, document.getElementById('mugo-app'));
