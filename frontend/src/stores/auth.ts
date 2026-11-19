import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../boot/axios'

export interface User {
  id: number
  username: string
  department: string
  full_name: string
  role_title?: string
  clearance_level?: string
  allowed_repos?: string[]
  is_admin?: boolean
  is_owner?: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const users = ref<User[]>([
    {
      id: 1,
      username: 'ananya',
      department: 'Product',
      full_name: 'Ananya Iyer',
      role_title: 'Platform Admin (Senior PM)',
      clearance_level: 'Master Admin Clearance',
      allowed_repos: ['Product Vault', 'Technical Specs', 'Sales Decks', 'Operations SOPs', 'Finance Rate Cards', 'Infosec Audit'],
      is_admin: true,
      is_owner: true,
    },
    {
      id: 2,
      username: 'aarav',
      department: 'Operations',
      full_name: 'Aarav Sharma',
      role_title: 'Operations Lead (Dept Owner)',
      clearance_level: 'Department Owner Clearance',
      allowed_repos: ['Bloomfire SOPs', 'Customer Dispute Handling', 'Operations Guides'],
      is_admin: false,
      is_owner: true,
    },
    {
      id: 3,
      username: 'priya',
      department: 'Sales',
      full_name: 'Priya Patel',
      role_title: 'Sales Lead (Dept Owner)',
      clearance_level: 'Department Owner Clearance',
      allowed_repos: ['Sales Pitch Decks', 'Enterprise Commercial Tiers', 'Bloomfire SOPs'],
      is_admin: false,
      is_owner: true,
    },
    {
      id: 4,
      username: 'rohan',
      department: 'Product',
      full_name: 'Rohan Verma',
      role_title: 'Product Analyst (Read-Only)',
      clearance_level: 'Analyst Clearance (Read-Only)',
      allowed_repos: ['Product Vault', 'Technical Specs', 'Sales Decks', 'Operations SOPs', 'Finance Rate Cards', 'Infosec Audit'],
      is_admin: false,
      is_owner: false,
    },
    {
      id: 5,
      username: 'chirag',
      department: 'Technical',
      full_name: 'Chirag Mehta',
      role_title: 'Systems Architect (Dept Owner)',
      clearance_level: 'Department Owner Clearance',
      allowed_repos: ['API Gateway Specs', 'mTLS Architecture', 'Bloomfire SOPs'],
      is_admin: false,
      is_owner: true,
    },
    {
      id: 6,
      username: 'vikram',
      department: 'Governance_Risk',
      full_name: 'Vikram Malhotra',
      role_title: 'Head of Infosec (Security Admin)',
      clearance_level: 'Master Security Admin Clearance',
      allowed_repos: ['ALL Repositories', 'Zero-PII Audit Trail', 'Retention & Governance'],
      is_admin: true,
      is_owner: true,
    },
    {
      id: 7,
      username: 'farhan',
      department: 'Finance',
      full_name: 'Farhan Qureshi',
      role_title: 'Pricing Controller (Dept Owner)',
      clearance_level: 'Department Owner Clearance',
      allowed_repos: ['Finance Rate Cards', 'Bureau Billing Tiers', 'Bloomfire SOPs'],
      is_admin: false,
      is_owner: true,
    },
  ])

  // Check saved session in localStorage
  const savedUserJson = localStorage.getItem('kmp_auth_user')
  const initialUser = savedUserJson ? JSON.parse(savedUserJson) : users.value[0]
  const initialAuth = localStorage.getItem('kmp_is_authenticated') === 'true'

  const currentUser = ref<User>(initialUser)
  const isAuthenticated = ref<boolean>(initialAuth)
  const activeView = ref<'chat' | 'admin'>(initialUser?.is_admin ? 'admin' : 'chat')

  const isPlatformAdmin = computed(() => {
    return Boolean(currentUser.value.is_admin) || ['ananya', 'vikram'].includes(currentUser.value.username)
  })

  const isDepartmentOwner = computed(() => {
    return Boolean(currentUser.value.is_owner)
  })

  const canUploadDocuments = computed(() => {
    return true
  })

  function canUploadToDepartment(targetDept: string): boolean {
    return true
  }

  const departmentColors: Record<string, string> = {
    Product: '#0A84FF',
    Operations: '#30D158',
    Technical: '#64D2FF',
    Sales: '#FF9F0A',
    Governance_Risk: '#BF5AF2',
    Infosec: '#BF5AF2',
    Finance: '#FFD60A',
    Bloomfire: '#0A84FF'
  }

  const currentDeptColor = computed(() => departmentColors[currentUser.value.department] || '#0A84FF')

  async function fetchUsers() {
    try {
      const res = await api.get('/api/users')
      if (res.data?.users && res.data.users.length > 0) {
        users.value = res.data.users.map((u: any) => {
          const matched = users.value.find(orig => orig.username === u.username)
          return {
            ...u,
            role_title: matched?.role_title || `${u.department} Specialist`,
            clearance_level: matched?.clearance_level || 'Level 2 - Standard',
            allowed_repos: matched?.allowed_repos || [u.department, 'Bloomfire SOPs']
          }
        })
        const found = users.value.find(u => u.username === currentUser.value.username)
        if (found) currentUser.value = found
      }
    } catch (err) {
      console.warn('Could not fetch users, using configured roles.', err)
    }
  }

  function login(user: User, view?: 'chat' | 'admin') {
    currentUser.value = user
    isAuthenticated.value = true
    const isAdmin = Boolean(user.is_admin) || ['ananya', 'vikram'].includes(user.username)
    if (!isAdmin) {
      activeView.value = 'chat'
    } else {
      activeView.value = view || 'admin'
    }
    localStorage.setItem('kmp_auth_user', JSON.stringify(user))
    localStorage.setItem('kmp_is_authenticated', 'true')
  }

  function logout() {
    isAuthenticated.value = false
    activeView.value = 'chat'
    localStorage.removeItem('kmp_is_authenticated')
  }

  function setUser(user: User) {
    currentUser.value = user
    const isAdmin = Boolean(user.is_admin) || ['ananya', 'vikram'].includes(user.username)
    if (!isAdmin) {
      activeView.value = 'chat'
    }
    localStorage.setItem('kmp_auth_user', JSON.stringify(user))
  }

  return {
    users,
    currentUser,
    isAuthenticated,
    activeView,
    isPlatformAdmin,
    isDepartmentOwner,
    canUploadDocuments,
    canUploadToDepartment,
    departmentColors,
    currentDeptColor,
    fetchUsers,
    login,
    logout,
    setUser,
  }
})
