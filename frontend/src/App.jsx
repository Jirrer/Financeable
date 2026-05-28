import { useState, useEffect } from 'react'
import './App.css'
import { Line, Pie } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

function App() {
	const [username, setusername] = useState('')
	const [password, setPassword] = useState('')
	const [rememberMe, setRememberMe] = useState(true)
	const [showRegister, setShowRegister] = useState(false)
	const [email, setEmail] = useState('')
	const [error, setError] = useState('')
	const [isLoggedIn, setIsLoggedIn] = useState(false)
	const [activeScreen, setActiveScreen] = useState('Reports')
	const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
	const [purchseChartData, setPurchaseChartData] = useState(null)
	const [incomeChartData, setIncomeChartData] = useState(null)
    const [historyChartData, setHistoryChartData] = useState(null)
	const defaultMonth = new Date().toISOString().slice(0,7) // YYYY-MM
	const [selectedMonth, setSelectedMonth] = useState(defaultMonth)
    const [historyMonthOne, setHistoryMonthOne] = useState(defaultMonth)
    const [historyMonthTwo, setHistoryMonthTwo] = useState(defaultMonth)

	async function handleSubmit(event) {
		event.preventDefault()

		if (!username.trim() || !password.trim()) {
			setError('Enter your username and password to continue.')
			return
		}

		const loginResponse = await login()

		if (loginResponse && loginResponse.ok) {
			setError('')
			setIsLoggedIn(true)
			setActiveScreen('Reports')
		} else if (loginResponse) {
			try {
				const loginData = await loginResponse.json()
				setError(loginData.error || loginData.message || 'Login failed')
			} catch (e) {
				setError('Login failed')
			}
		}
	}

	async function login() {
		const url = `${apiBaseUrl}/login`

		try {
			const response = await fetch(url, {
				method: 'POST',
				credentials: 'include', 
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: username.trim(), password }),
			})

			return response
		} catch (err) {
			console.warn('Backend fetch failed', err)
			return null
		}
	}

	async function register() {
		const url = `${apiBaseUrl}/register`

		if (!username.trim() || !password) {
			setError('Enter username and password to register')
			return null
		}

		try {
			const registerResponse = await fetch(url, {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: username.trim(), password, email: email?.trim() || null }),
			})

			if (registerResponse.ok) {
				setShowRegister(false)
				setIsLoggedIn(true)
				return registerResponse
			}

			try {
				const registerData = await registerResponse.json()
				setError(registerData.error || registerData.message || 'Registration failed')
			} catch (e) {
				setError('Registration failed')
			}
			return response
		} catch (err) {
			console.warn('Backend fetch failed', err)
			setError('Registration failed')
			return null
		}
	}

    async function logOut() {
		await fetch(`${apiBaseUrl}/logout`, { method: 'POST', credentials: 'include' });
		setIsLoggedIn(false);
		setusername('');
	}

	async function getMonth(month = selectedMonth) {
		const url = `${apiBaseUrl}/get-report?`

		try {
			const response = await fetch(url, {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify({ input_type: 'month', date: selectedMonth, return_type: 'json' })
				})

			if (response.ok) {
				const json = await response.json()

				const report = json?.report ?? json
				let purchaseData = null
				let incomeData = null

				if (report && report.purchase && typeof report.purchase === 'object' && Object.keys(report.purchase).length) {
					const labels = Object.keys(report.purchase)
					const values = labels.map((k) => Math.abs(Number(report.purchase[k] ?? 0)))
					const colors = ['#0ea5e9', '#60a5fa', '#34d399', '#f97316', '#f43f5e']
					purchaseData = { labels, datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length), borderColor: '#fff', borderWidth: 1 }] }
				}

				if (report && report.income && typeof report.income === 'object' && Object.keys(report.income).length) {
					const ilabels = Object.keys(report.income)
					const ivalues = ilabels.map((k) => Math.abs(Number(report.income[k] ?? 0)))
					const colors = ['#34d399', '#60a5fa', '#0ea5e9', '#f97316', '#f43f5e']
					incomeData = { labels: ilabels, datasets: [{ data: ivalues, backgroundColor: colors.slice(0, ilabels.length), borderColor: '#fff', borderWidth: 1 }] }
				}

				return { selectedMonth, purchaseData, incomeData, report }
			} else {
				console.warn('Backend returned non-ok', response.status)
			}
		} catch (err) {
			console.warn('Backend fetch failed', err)
		}

		return { selectedMonth, purchaseData: null, incomeData: null, report: null }
	}

    async function getHistory(monthStart = historyMonthOne, monthEnd = historyMonthTwo) {
        return { data: null }

		const id = 1
		const input_type = 'history'
		const date = monthStart
		const return_type = 'json'

		const url = `${apiBaseUrl}/get-history?id=${encodeURIComponent(id)}&input_type=${encodeURIComponent(input_type)}&date=${encodeURIComponent(date)}&return_type=${encodeURIComponent(return_type)}`

		try {
			const response = await fetch(url)
			if (response.ok) {
				const json = await response.json()

				data = null

				if (report && report.purchase && typeof report.purchase === 'object' && Object.keys(report.purchase).length) {
					const labels = Object.keys(report.purchase)
					const values = labels.map((k) => Math.abs(Number(report.purchase[k] ?? 0)))
					const colors = ['#0ea5e9', '#60a5fa', '#34d399', '#f97316', '#f43f5e']
					purchaseData = { labels, datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length), borderColor: '#fff', borderWidth: 1 }] }
				}

				if (report && report.income && typeof report.income === 'object' && Object.keys(report.income).length) {
					const ilabels = Object.keys(report.income)
					const ivalues = ilabels.map((k) => Math.abs(Number(report.income[k] ?? 0)))
					const colors = ['#34d399', '#60a5fa', '#0ea5e9', '#f97316', '#f43f5e']
					incomeData = { labels: ilabels, datasets: [{ data: ivalues, backgroundColor: colors.slice(0, ilabels.length), borderColor: '#fff', borderWidth: 1 }] }
				}

				return { data: null }
			} else {
				console.warn('Backend returned non-ok', response.status)
			}
		} catch (err) {
			console.warn('Backend fetch failed', err)
		}

		return { data }
	}

	useEffect(() => {
		if (!isLoggedIn || activeScreen !== 'Reports') {
			return
		}

		if (activeScreen === 'Reports') {
			let mounted = true

			getMonth(selectedMonth).then((res) => {
				if (!mounted) return
				setPurchaseChartData(res.purchaseData)
				setIncomeChartData(res.incomeData)
			})

            mounted = true
            getHistory(historyMonthOne, historyMonthTwo).then((res) => {
				if (!mounted) return
				setHistoryChartData(res.data)
			})

			return () => {
				mounted = false
			}
		}
	}, [isLoggedIn, selectedMonth, activeScreen, historyMonthOne, historyMonthTwo])

	if (isLoggedIn) {
		const screenTitle = activeScreen === 'Reports' ? 'Reports' : 'Log-Data'

		return (
			<main className="app-shell">
				<header className="top-bar">
					<div>
                        <div>
                            {username}
                            <button onClick={logOut}>Sign Out</button>
                        </div>						
					</div>

					<nav className="top-bar-actions" aria-label="Dashboard screens">
						<button
							type="button"
							className={`screen-button ${activeScreen === 'Reports' ? 'active' : ''}`}
							onClick={() => setActiveScreen('Reports')}
						>
							Reports
						</button>
						<button
							type="button"
							className={`screen-button ${activeScreen === 'Log-Data' ? 'active' : ''}`}
							onClick={() => setActiveScreen('Log-Data')}
						>
							Log Data
						</button>
					</nav>
				</header>

				<section className="screen-card">
					{activeScreen === 'Reports' && (
						<div>
						<h2>Reports</h2>
						<label style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}>
							<input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} />
						</label>
						<div className="dual-charts">
							<div className="chart-block">
								<p className="chart-label">Purchases</p>
								<div className="chart-container">
									{purchseChartData ? (
										<Pie
											data={purchseChartData}
											options={{
												responsive: true,
												maintainAspectRatio: false,
												plugins: { legend: { position: 'bottom' } },
											}}
										/>
									) : (
										<div className="empty-state">No purchase data yet.</div>
									)}
								</div>
							</div>

							<div className="chart-block">
								<p className="chart-label">Income</p>
								<div className="chart-container">
									{incomeChartData ? (
										<Pie
											data={incomeChartData}
											options={{
												responsive: true,
												maintainAspectRatio: false,
												plugins: { legend: { position: 'bottom' } },
											}}
										/>
									) : (
										<div className="empty-state">No income data yet.</div>
									)}
								</div>
							</div>

                            <div className="chart-block">
								<p className="chart-label">History</p>
								<div className="chart-container">
									{historyChartData ? (
										<Line
											data={historyChartData}
											options={{
												responsive: true,
												maintainAspectRatio: false,
												plugins: { legend: { position: 'bottom' } },
											}}
										/>
									) : (
										<div className="empty-state">No history data yet.</div>
									)}
								</div>
							</div>
						</div>
						</div>
                        
					)}

                    {activeScreen === 'Log-Data' && (
                        <div>
                        <h2>Activity</h2>
                        <div>Activity content here</div>
                        </div>
                    )}
                    </section>
			</main>
		)
	}

	return (
		<main className="page-shell">
			<section className="login-layout">
				<form className="login-card" onSubmit={handleSubmit} noValidate>
					<div>
						<h2>Sign in</h2>
					</div>

					<label className="field">
						<span>username</span>
						<input
							type="username"
							value={username}
							onChange={(event) => setusername(event.target.value)}
							placeholder="Enter you username"
							autoComplete="username"
						/>
					</label>

					<label className="field">
						<span>Password</span>
						<input
							type="password"
							value={password}
							onChange={(event) => setPassword(event.target.value)}
							placeholder="Enter your password"
							autoComplete="current-password"
						/>
					</label>
					{error ? <p className="error-message">{error}</p> : null}
						{showRegister ? (
							<>
								<label className="field">
									<span>Email (optional)</span>
									<input
										type="username"
										value={email}
										onChange={(e) => setEmail(e.target.value)}
										placeholder="username"
										autoComplete="username"
									/>
									</label>

								<button
									type="button"
									className="primary-button"
									onClick={async () => {
										const resp = await register()
										if (resp && resp.ok) {
											setError('')
											setIsLoggedIn(true)
											setActiveScreen('Reports')
										}
									}}
								>
									Register
								</button>

								<button type="button" className="link-button" onClick={() => setShowRegister(false)}>
									Cancel
								</button>
							</>
						) : (
							<>
								<button type="submit" className="primary-button">
									Sign in
								</button>
								<button type="button" className="link-button" onClick={() => setShowRegister(true)}>
									Create account
								</button>
							</>
						)}

				</form>
			</section>
		</main>
	)

}

export default App