import { ComponentProps, createContext, useContext, useState } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface SidebarContextType {
  isCollapsed: boolean
  setIsCollapsed: (collapsed: boolean) => void
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined)

function useSidebar() {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

interface SidebarProps extends ComponentProps<"div"> {
  defaultCollapsed?: boolean
}

function Sidebar({ className, children, defaultCollapsed = false, ...props }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  return (
    <SidebarContext.Provider value={{ isCollapsed, setIsCollapsed }}>
      <div
        className={cn(
          "flex h-screen flex-col border-r bg-background transition-all duration-300",
          isCollapsed ? "w-16" : "w-64",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  )
}

function SidebarHeader({ className, children, ...props }: ComponentProps<"div">) {
  const { isCollapsed } = useSidebar()

  return (
    <div
      className={cn(
        "flex items-center border-b px-4 py-4",
        isCollapsed ? "justify-center" : "justify-between",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

function SidebarContent({ className, children, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn("flex-1 overflow-y-auto px-2 py-4", className)}
      {...props}
    >
      {children}
    </div>
  )
}

function SidebarFooter({ className, children, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn("border-t px-4 py-4", className)}
      {...props}
    >
      {children}
    </div>
  )
}

interface SidebarItemProps extends ComponentProps<"button"> {
  icon?: React.ReactNode
  label: string
  isActive?: boolean
  badge?: string | number
}

function SidebarItem({ 
  className, 
  icon, 
  label, 
  isActive = false, 
  badge,
  children,
  ...props 
}: SidebarItemProps) {
  const { isCollapsed } = useSidebar()

  return (
    <button
      className={cn(
        "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors",
        "hover:bg-accent hover:text-accent-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        isActive && "bg-accent text-accent-foreground",
        isCollapsed && "justify-center px-2",
        className
      )}
      title={isCollapsed ? label : undefined}
      {...props}
    >
      {icon && (
        <span className="flex-shrink-0">
          {icon}
        </span>
      )}
      
      {!isCollapsed && (
        <>
          <span className="flex-1 truncate">{label}</span>
          {badge && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
              {badge}
            </span>
          )}
        </>
      )}
      
      {children}
    </button>
  )
}

function SidebarGroup({ className, children, title, ...props }: ComponentProps<"div"> & { title?: string }) {
  const { isCollapsed } = useSidebar()

  return (
    <div className={cn("space-y-1", className)} {...props}>
      {title && !isCollapsed && (
        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {title}
        </div>
      )}
      {children}
    </div>
  )
}

function SidebarToggle({ className, ...props }: ComponentProps<typeof Button>) {
  const { isCollapsed, setIsCollapsed } = useSidebar()

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setIsCollapsed(!isCollapsed)}
      className={cn("h-8 w-8 p-0", className)}
      {...props}
    >
      {isCollapsed ? (
        <ChevronRight className="h-4 w-4" />
      ) : (
        <ChevronLeft className="h-4 w-4" />
      )}
    </Button>
  )
}

export {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarItem,
  SidebarGroup,
  SidebarToggle,
  useSidebar,
}